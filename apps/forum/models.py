"""
Data models for the forum app.
"""

from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel

from apps.fileattachments.models import FileAttachment
from apps.tools.fields import (AutoOneToOneField,
                               AutoResizingImageField)
from apps.tools.utils import unique_slug
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_document
from apps.txtrender.signals import render_engine_changed


from .settings import (NB_FORUM_POST_PER_PAGE,
                       NB_SECONDS_BETWEEN_POSTS,
                       FORUM_LOGO_HEIGHT_SIZE_PX,
                       FORUM_LOGO_WIDTH_SIZE_PX,
                       FORUM_LOGO_UPLOAD_DIR_NAME,
                       NB_DAYS_BEFORE_FORUM_POST_GET_OLD)
from .managers import (ForumManager,
                       ForumThreadManager,
                       ForumThreadPostManager,
                       ForumSubscriptionManager,
                       ForumThreadSubscriptionManager,
                       ReadForumTrackerManager,
                       ReadForumThreadTrackerManager)


class Forum(MPTTModel):
    """
    Forum main data model.
    A forum is made of:
    - a title (human readable) and a slug (SEO/machine readable),
    - an optional logo,
    - a description (can be blank),
    - a "private" flag, if set the forum is only visible by staff.
    - a "closed" flag, for read-only forum,
    - a parent forum, or null if root forum.
    """

    title = models.CharField(_('Title'),
                             max_length=255)

    # FIXME AutoSlugField
    slug = models.SlugField(_('Slug'),
                            max_length=255)

    slug_hierarchy = models.SlugField(_('Slug hierarchy'),
                                      max_length=1023,
                                      unique=True)

    logo = AutoResizingImageField(_('Logo'),
                                  upload_to=FORUM_LOGO_UPLOAD_DIR_NAME,
                                  width=FORUM_LOGO_WIDTH_SIZE_PX,
                                  height=FORUM_LOGO_HEIGHT_SIZE_PX,
                                  default=None,
                                  blank=True,
                                  null=True)

    description = RenderTextField(_('Description'))

    description_html = models.TextField(_('Description (raw HTML)'))

    description_text = models.TextField(_('Description (raw text)'))

    private = models.BooleanField(_('Private'),
                                  default=False)

    closed = models.BooleanField(_('Closed'),
                                 default=False)

    parent = models.ForeignKey('self',
                               db_index=True,  # Database optimization
                               related_name='children',
                               verbose_name=_('Parent forum'),
                               default=None,
                               blank=True,
                               null=True)

    ordering = models.IntegerField(_('Ordering'),
                                   db_index=True,  # Database optimization
                                   default=1)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    objects = ForumManager()

    class MPTTMeta:
        order_insertion_by = ('ordering', 'title')

    class Meta:
        unique_together = (('slug', 'parent'), )
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')
        ordering = ('ordering', 'title')
        permissions = (('can_see_private_forum', 'Can see private forum'), )

    def save(self, *args, **kwargs):
        """
        Save the model
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(Forum, self, self.slug, 'slug', self.title, {'parent': self.parent})

        # Render the description
        self.render_description()

        # Build complete slug hierarchy
        self.build_slug_hierarchy()

        # Save the forum
        super(Forum, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug_hierarchy

    def get_absolute_url(self):
        """
        Return the permalink to this forum.
        """
        return reverse('forum:forum_detail', kwargs={'hierarchy': self.slug_hierarchy})

    def get_create_thread_url(self):
        """
        Return the "create thread" permalink for this forum.
        """
        return reverse('forum:thread_create', kwargs={'hierarchy': self.slug_hierarchy})

    def get_mark_all_threads_as_read_url(self):
        """
        Return the "mark all threads as read" permalink for this forum.
        """
        return reverse('forum:forum_mark_all_threads_as_read', kwargs={'hierarchy': self.slug_hierarchy})

    def get_subscribe_url(self):
        """
        Return the "subscribe" permalink for this forum.
        """
        return reverse('forum:forum_subscribe', kwargs={'hierarchy': self.slug_hierarchy})

    def get_unsubscribe_url(self):
        """
        Return the "un-subscribe" permalink for this forum.
        """
        return reverse('forum:forum_unsubscribe', kwargs={'hierarchy': self.slug_hierarchy})

    def get_latest_threads_rss_feed_url(self):
        """
        Return the permalink to "latest threads" RSS feed for this thread.
        """
        return reverse('forum:latest_forum_threads_for_forum_rss', kwargs={'hierarchy': self.slug_hierarchy})

    def get_latest_threads_atom_feed_url(self):
        """
        Return the permalink to "latest threads" Atom feed for this thread.
        """
        return reverse('forum:latest_forum_threads_for_forum_atom', kwargs={'hierarchy': self.slug_hierarchy})

    def get_latest_posts_rss_feed_url(self):
        """
        Return the permalink to "latest posts" RSS feed for this thread.
        """
        return reverse('forum:latest_forum_thread_posts_for_forum_rss', kwargs={'hierarchy': self.slug_hierarchy})

    def get_latest_posts_atom_feed_url(self):
        """
        Return the permalink to "latest posts" Atom feed for this thread.
        """
        return reverse('forum:latest_forum_thread_posts_for_forum_atom', kwargs={'hierarchy': self.slug_hierarchy})

    def build_slug_hierarchy(self, save=False):
        """
        Pre-compute the slug hierarchy of this category. Save the model if ``save`` is True.
        """

        # Compute the slug hierarchy
        self.slug_hierarchy = '%s/%s' % (self.parent.slug_hierarchy, self.slug) if self.parent else self.slug

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            # Include MPTT fields in the ``update_fields`` arguments to avoid messing up the tree
            super(Forum, self).save(update_fields=('slug_hierarchy',
                                                   'parent',
                                                   'level',
                                                   'lft',
                                                   'rght',
                                                   'tree_id'))

    def set_closed(self, closed, close_threads=False, recursive=False, save=False):
        """
        Set the "closed" flag of this forum (and child forums is ``recursive=True``, default False).
        Can also closed all threads in this forum if ``close_threads=True`` (default False).
        :param closed: "closed" flag state (bool)
        :param close_threads: Set to ``True`` to also close all threads in this forum.
        :param recursive: Set to ``True`` to recursively set the "closed" flag to child forums.
        :param save: Set to True to save the model instance after setting up the closed flag.
        """
        self.closed = closed
        if close_threads:
            self.threads.all().update(closed=closed)
        if recursive:
            for forum in self.children.all():
                forum.set_closed(closed, close_threads, recursive, save=True)
        if save:
            self.save(update_fields=('closed', ))

    def set_private(self, private, recursive=False, save=False):
        """
        Set the "private" flag of this forum (and child forums is ``recursive=True``).
        :param private: "private" flag state (bool)
        :param recursive: Set to ``True`` to recursively set the "private" flag to child forums.
        :param save: Set to True to save the model instance after setting up the private flag.
        """
        self.private = private
        if recursive:
            for forum in self.children.all():
                forum.set_private(private, recursive, save=True)
        if save:
            self.save(update_fields=('private', ))

    def has_access(self, user):
        """
        Return True if the given user has access to this forum.
        """
        return user.has_perm('forum.can_see_private_forum') if self.private else True

    def render_description(self, save=False):
        """
        Render the content. Save the model only if ``save`` is True.
        """

        # Render HTML
        content_html, content_text, _ = render_document(self.content,
                                                        allow_text_formating=True,
                                                        allow_text_extra=True,
                                                        allow_text_alignments=True,
                                                        allow_text_directions=True,
                                                        allow_text_modifiers=True,
                                                        allow_text_colors=True,
                                                        allow_spoilers=True,
                                                        allow_lists=True,
                                                        allow_definition_lists=True,
                                                        allow_acronyms=True,
                                                        allow_links=True,
                                                        allow_cdm_extra=True,
                                                        force_nofollow=False,
                                                        render_text_version=True)
        self.description_html = content_html
        self.description_text = content_text

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(Forum, self).save(update_fields=('description_html', 'description_text'))


def _redo_forum_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all forums.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for forum in Forum.objects.all():
        forum.render_description(save=True)

render_engine_changed.connect(_redo_forum_text_rendering)


def update_child_forum_slug_hierarchy_on_parent_save(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    Update any child forum's slug hierarchy on parent save.
    :param sender: The Forum class.
    :param instance: The forum instance.
    :param created: True if the instance just been created.
    :param raw: True if the instance is saved as-is and should not be used.
    :param using: The database alias.
    :param update_fields: Not used.
    :param kwargs: Any extra keywords arguments.
    :return: None
    """

    # Don't do useless stuff
    if created or raw:
        return

    # Update child forums
    for child in instance.children.all():
        child.build_slug_hierarchy(save=True)

post_save.connect(update_child_forum_slug_hierarchy_on_parent_save, sender=Forum)


class ForumThread(models.Model):
    """
    Forum's thread data model.
    A forum's thread is made of:
    - a title (human readable),
    - a slug, not unique required because the url are prefixed with the PK.
    - a parent forum, all child threads are available using the ``threads`` of ``Forum`` class.
    - a "sticky" flag,
    - a "closed" flag, for closed thread (no more post allowed),
    - a "locked" flag, for closed thread set by admin,
    - a "resolved" flag, for resolved issue/problem,
    - a first and last post reference.
    """

    title = models.CharField(_('Title'),
                             max_length=255)

    # FIXME AutoSlugField (non unique)
    slug = models.SlugField(_('Slug'),
                            max_length=255)  # NOT unique, use urls like PK-SLUG

    parent_forum = models.ForeignKey(Forum,
                                     db_index=True,  # Database optimization
                                     related_name='threads',
                                     verbose_name=_('Parent forum'))

    sticky = models.BooleanField(_('Sticky'),
                                 default=False)

    global_sticky = models.BooleanField(_('Global sticky'),
                                        default=False)

    closed = models.BooleanField(_('Closed'),
                                 default=False)

    resolved = models.BooleanField(_('Resolved'),
                                   default=False)

    locked = models.BooleanField(_('Locked'),
                                 default=False)

    first_post = models.ForeignKey('ForumThreadPost',
                                   related_name='first_post_of+',
                                   verbose_name=_('First post'))

    last_post = models.ForeignKey('ForumThreadPost',
                                  related_name='last_post_of+',
                                  verbose_name=_('Last post'))

    deleted_at = models.DateTimeField(_('Deletion date'),
                                      db_index=True,  # Database optimization
                                      default=None,
                                      blank=True,
                                      null=True)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    objects = ForumThreadManager()

    class Meta:
        verbose_name = _('Forum thread')
        verbose_name_plural = _('Forum threads')
        get_latest_by = 'last_post__last_modification_date'
        ordering = ('-last_post__last_modification_date', 'title')

    def save(self, *args, **kwargs):
        """
        Save the model.
        :param args: for super()
        :param kwargs: for super()
        """

        # Compute slug
        if not self.slug:
            self.slug = slugify(self.title)

        # Set sticky flag if global sticky set
        if self.global_sticky:
            self.sticky = True

        # Save the model
        super(ForumThread, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return the permalink to this forum's thread.
        """
        return reverse('forum:thread_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_edit_url(self):
        """
        Return the "edit" permalink for this forum's thread.
        """
        return reverse('forum:thread_edit', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_delete_url(self):
        """
        Return the "delete" permalink for this forum's thread.
        """
        return reverse('forum:thread_delete', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_reply_url(self):
        """
        Return the "reply" permalink for this forum's thread.
        """
        return reverse('forum:thread_reply', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_subscribe_url(self):
        """
        Return the "subscribe" permalink for this forum's thread.
        """
        return reverse('forum:thread_subscribe', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_unsubscribe_url(self):
        """
        Return the "un-subscribe" permalink for this forum's thread.
        """
        return reverse('forum:thread_unsubscribe', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_latest_posts_rss_feed_url(self):
        """
        Return the permalink to "latest posts" RSS feed for this thread.
        """
        return reverse('forum:latest_forum_thread_posts_for_thread_rss', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_latest_posts_atom_feed_url(self):
        """
        Return the permalink to "latest posts" Atom feed for this thread.
        """
        return reverse('forum:latest_forum_thread_posts_for_thread_atom', kwargs={'pk': self.pk, 'slug': self.slug})

    def has_access(self, user):
        """
        Returns True if the user has access to the parent forum.
        """
        return self.parent_forum.has_access(user)

    def can_edit(self, user):
        """
        Return True if the given user can edit this thread. The user can edit the post if his is an admin
        """
        is_author = user == self.first_post.author
        has_edit_perm = user.has_perm('forum.change_forumthread')
        return is_author or has_edit_perm

    def can_delete(self, user):
        """
        Return True if the given user can delete this thread.
        """
        reply_count = self.posts.published().count()
        is_author = user == self.first_post.author
        has_del_perm = user.has_perm('forum.delete_forumthreadpost')
        return (is_author and reply_count <= 1) or has_del_perm

    def is_deleted(self):
        """
        Return True if the thread has been deleted.
        """
        return self.deleted_at is not None
    is_deleted.short_description = _('is deleted')
    is_deleted.boolean = True

    def is_old(self):
        """
        Return ``True`` if the last modification date of the last message
        is older than ``NB_DAYS_BEFORE_FORUM_POST_GET_OLD`` days.
        """
        last_update_date = self.last_post.last_content_modification_date or self.last_post.pub_date
        old_threshold_date = timezone.now() - timedelta(days=NB_DAYS_BEFORE_FORUM_POST_GET_OLD)
        return last_update_date < old_threshold_date
    is_old.boolean = True
    is_old.short_description = _('Old')


class ForumThreadPost(models.Model):
    """
    Forum thread's post data model.
    A forum's thread is made of:
    - a parent thread, can be null to allow the three steps thread and first post creation.
    - an author,
    - a published date,
    - a last modification date,
    - some text (source and HTML version),
    - the author's IP address (for legal purpose).
    """

    parent_thread = models.ForeignKey(ForumThread,
                                      db_index=True,  # Database optimization
                                      related_name='posts',
                                      verbose_name=_('Parent thread'),
                                      default=None,
                                      blank=True,
                                      null=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='forum_posts',
                               verbose_name=_('Author'))

    pub_date = models.DateTimeField(_('Publication date'),
                                    db_index=True)  # Database optimization

    last_content_modification_date = models.DateTimeField(_('Last content modification date'),
                                                          db_index=True)  # Database optimization

    last_modification_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                             related_name='+',
                                             verbose_name=_('Last modification by'),
                                             default=None,
                                             blank=True,
                                             null=True,
                                             on_delete=models.SET_NULL)

    content = RenderTextField(_('Content'))

    content_html = models.TextField(_('Content (raw HTML)'))

    content_text = models.TextField(_('Content (raw text)'))

    summary_html = models.TextField(_('Content summary (raw HTML)'))

    footnotes_html = models.TextField(_('Content footnotes (raw HTML)'))

    author_ip_address = models.GenericIPAddressField(_('Author IP address'),
                                                     default=None,
                                                     blank=True,
                                                     null=True)

    deleted_at = models.DateTimeField(_('Deletion date'),
                                      db_index=True,  # Database optimization
                                      default=None,
                                      blank=True,
                                      null=True)

    attachments = GenericRelation(FileAttachment,
                                  related_query_name='forum_posts')

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    objects = ForumThreadPostManager()

    class Meta:
        verbose_name = _('Forum post')
        verbose_name_plural = _('Forum posts')
        get_latest_by = 'pub_date'
        permissions = (
            ('can_see_ip_address', 'Can see IP address'),

            ('allow_titles_in_post', 'Allow titles in forum post'),
            ('allow_alerts_box_in_post', 'Allow alerts box in forum post'),
            ('allow_text_colors_in_post', 'Allow coloured text in forum post'),
            ('allow_cdm_extra_in_post', 'Allow CDM extra in forum post'),
            ('allow_raw_link_in_post', 'Allow raw link (without forcing nofollow) in forum post'),
        )
        ordering = ('-pub_date', )

    def __str__(self):
        return "Post from %s" % self.author.username

    def save(self, *args, **kwargs):
        """
        Save the model.
        :param current_user: The current user editing this post.
        :param args: for super()
        :param kwargs: for super()
        """

        # Handle last_modification_by
        self.last_modification_by = kwargs.pop('current_user', self.author)

        # Handle optional pub_date and refresh last_content_modification_date
        now = timezone.now()
        if not self.pub_date:
            self.pub_date = now
        if not self.last_content_modification_date:
            if now > self.pub_date:
                self.last_content_modification_date = now
            else:
                self.last_content_modification_date = self.pub_date
        elif now > self.last_content_modification_date:
            self.last_content_modification_date = now

        # Render the HTML version
        self.render_text()

        # Save the model
        super(ForumThreadPost, self).save(*args, **kwargs)

        # Reset parent last post
        self.reset_parent_last_post()

    def get_absolute_url(self):
        """
        Return the permalink to this post.
        """
        nb_posts_before_this_post = ForumThreadPost.objects.published() \
            .filter(parent_thread=self.parent_thread, id__lt=self.id) \
            .count()
        page_nb_for_this_post = (nb_posts_before_this_post + 1) // NB_FORUM_POST_PER_PAGE
        page_str = '?page=%d' % page_nb_for_this_post if page_nb_for_this_post > 0 else ''
        return '%s%s#post-%d' % (reverse('forum:thread_detail', kwargs={'pk': self.parent_thread.pk,
                                                                        'slug': self.parent_thread.slug}),
                                 page_str, self.id)

    def get_absolute_url_simple(self):
        """
        Return the permalink to this post, using the redirection detail view to avoid extra SQL query.
        """
        return reverse('forum:post_detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        """
        Return the "edit" permalink for this thread post.
        """
        return reverse('forum:post_edit', kwargs={'pk': self.pk})

    def get_delete_url(self):
        """
        Return the "delete" permalink for this thread post.
        """
        return reverse('forum:post_delete', kwargs={'pk': self.pk})

    def get_reply_url(self):
        """
        Return the "reply" permalink for this thread post.
        """
        return reverse('forum:post_reply', kwargs={'pk': self.pk})

    def get_report_url(self):
        """
        Return the "report" permalink for this thread post.
        """
        return reverse('forum:post_report', kwargs={'pk': self.pk})

    def is_first_post(self):
        """
        Return True if the current post if the first post of the parent thread.
        """
        return self == self.parent_thread.first_post

    def is_last_post(self):
        """
        Return True if the current post if the last post of the parent thread.
        """
        return self == self.parent_thread.last_post

    def can_edit(self, user):
        """
        Return True if the given user can edit this post. The user can edit the post if his is an admin.
        """
        return user == self.author or user.has_perm('forum.change_forumthreadpost')

    def can_delete(self, user):
        """
        Return True if the given user can delete this post. The user can delete the post if his is an admin.
        """
        return user == self.author or user.has_perm('forum.delete_forumthreadpost')

    def can_see_ip_adress(self, user):
        """
        Return True if the given user can see the IP address of the author of this post.
        """
        return user == self.author or user.has_perm('forum.can_see_ip_address')

    def is_deleted(self):
        """
        Return True if the post has been deleted.
        """
        return self.deleted_at is not None

    is_deleted.short_description = _('is deleted')
    is_deleted.boolean = True

    def has_been_modified_after_publication(self):
        """
        Return True if the post has been modified after publication.
        """
        return self.last_content_modification_date is not None and \
               self.last_content_modification_date != self.pub_date

    def reset_parent_last_post(self):
        """
        Reset the parent thread last post instance.
        """
        parent_thread = self.parent_thread
        if parent_thread is not None:
            parent_thread.last_post = parent_thread.posts.published().order_by('pub_date').last()
            print(parent_thread)
            print(parent_thread.last_post)
            parent_thread.save(update_fields=('last_post',))

    def render_text(self, save=False):
        """
        Render the content. Save the model only if ``save`` is True.
        """

        # Render HTML
        allow_titles_in_post = self.author.has_perm('forum.allow_titles_in_post')
        allow_alerts_box_in_post = self.author.has_perm('forum.allow_alerts_box_in_post')
        allow_text_colors_in_post = self.author.has_perm('forum.allow_text_colors_in_post')
        allow_cdm_extra_in_post = self.author.has_perm('forum.allow_cdm_extra_in_post')
        force_nofollow_in_post = not self.author.has_perm('forum.allow_raw_link_in_post')
        content_html, content_text, extra_dict = render_document(self.content,
                                                                 allow_titles=allow_titles_in_post,
                                                                 allow_code_blocks=True,
                                                                 allow_alerts_box=allow_alerts_box_in_post,
                                                                 allow_text_formating=True,
                                                                 allow_text_extra=True,
                                                                 allow_text_alignments=True,
                                                                 allow_text_directions=True,
                                                                 allow_text_modifiers=True,
                                                                 allow_text_colors=allow_text_colors_in_post,
                                                                 allow_spoilers=True,
                                                                 allow_figures=True,
                                                                 allow_lists=True,
                                                                 allow_todo_lists=True,
                                                                 allow_definition_lists=True,
                                                                 allow_tables=True,
                                                                 allow_quotes=True,
                                                                 allow_footnotes=True,
                                                                 allow_acronyms=True,
                                                                 allow_links=True,
                                                                 allow_medias=True,
                                                                 allow_cdm_extra=allow_cdm_extra_in_post,
                                                                 force_nofollow=force_nofollow_in_post,
                                                                 render_text_version=True,
                                                                 render_extra_dict=True,
                                                                 merge_footnotes_html=True,
                                                                 merge_footnotes_text=True)
        self.content_html = content_html
        self.content_text = content_text
        self.summary_html = extra_dict['summary_html'] if allow_titles_in_post else ''
        self.footnotes_html = extra_dict['footnotes_html']

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(ForumThreadPost, self).save(update_fields=('content_html', 'content_text',
                                                             'summary_html', 'footnotes_html'))


def _redo_forum_thread_posts_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all forum posts.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for post in ForumThreadPost.objects.all():
        post.render_text(save=True)

render_engine_changed.connect(_redo_forum_thread_posts_text_rendering)


def update_last_post_of_parent_thread_before_deleting_post(sender, instance, using, **kwargs):
    """
    Update the ``last_post`` instance of the parent thread on post delete if the given post instance is the last post
    of the parent thread (and not the first post).
    :param sender: The ForumThreadPost class.
    :param instance: The post instance to be deleted.
    :param using: The database used.
    :return: None
    """
    parent_thread = instance.parent_thread
    if instance.is_last_post() and not instance.is_first_post():
        parent_thread.last_post = parent_thread.posts.exclude(pk=instance.pk).last()
        parent_thread.save()


pre_delete.connect(update_last_post_of_parent_thread_before_deleting_post, sender=ForumThreadPost)


class ForumSubscription(models.Model):
    """
    Forum subscription model.
    A forum subscription is made of:
    - a related forum,
    - a related user,
    - an "active" flag used to avoid creating/deleting subscription entry multiple time on PEBCAK.
    """

    forum = models.ForeignKey(Forum,
                              db_index=True,  # Database optimization
                              editable=False,
                              related_name='subscribers',
                              verbose_name=_('Related forum'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,  # Database optimization
                             editable=False,
                             related_name='forum_subscriptions',
                             verbose_name=_('Subscriber'))

    active = models.BooleanField(_('Active'),
                                 default=True)

    objects = ForumSubscriptionManager()

    class Meta:
        unique_together = (('forum', 'user'),)
        verbose_name = _('Forum subscription')
        verbose_name_plural = _('Forum subscriptions')

    def __str__(self):
        return 'Subscription of "%s" for forum #%d' % (self.user.username, self.forum.pk)


class ForumThreadSubscription(models.Model):
    """
    Forum thread subscription model.
    A forum's thread subscription is made of:
    - a related thread,
    - a related user,
    - an "active" flag used to avoid creating/deleting subscription entry multiple time on PEBCAK.
    """

    thread = models.ForeignKey(ForumThread,
                               db_index=True,  # Database optimization
                               editable=False,
                               related_name='subscribers',
                               verbose_name=_('Related thread'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,  # Database optimization
                             editable=False,
                             related_name='forum_thread_subscriptions',
                             verbose_name=_('Subscriber'))

    active = models.BooleanField(_('Active'),
                                 default=True)

    objects = ForumThreadSubscriptionManager()

    class Meta:
        unique_together = (('thread', 'user'),)
        verbose_name = _('Forum thread subscription')
        verbose_name_plural = _('Forum thread subscriptions')

    def __str__(self):
        return 'Subscription of "%s" for thread #%d' % (self.user.username, self.thread.pk)


class ReadForumTracker(models.Model):
    """
    Model for tracking read/unread forum.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,  # Database optimization
                             editable=False,
                             related_name='+',
                             verbose_name=_('Related user'))

    forum = models.ForeignKey('Forum',
                              db_index=True,  # Database optimization
                              editable=False,
                              related_name='+',
                              verbose_name=_('Related forum'))

    last_read_date = models.DateTimeField(_('Last read date'))

    active = models.BooleanField(_('Active'),
                                 default=True)

    objects = ReadForumTrackerManager()

    class Meta:
        unique_together = (('forum', 'user'),)
        verbose_name = _('Read forum tracker')
        verbose_name_plural = _('Read forum trackers')

    def save(self, *args, **kwargs):
        """
        Save the model.
        """

        # Set the last read date if not set
        if self.last_read_date is None:
            self.last_read_date = timezone.now()

        # Save the model
        super(ReadForumTracker, self).save(*args, **kwargs)


class ReadForumThreadTracker(models.Model):
    """
    Model for tracking read/unread forum's thread.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,  # Database optimization
                             editable=False,
                             related_name='+',
                             verbose_name=_('Related user'))

    thread = models.ForeignKey('ForumThread',
                               db_index=True,  # Database optimization
                               editable=False,
                               related_name='+',
                               verbose_name=_('Related forum thread'))

    last_read_date = models.DateTimeField(_('Last read date'))

    active = models.BooleanField(_('Active'),
                                 default=True)

    objects = ReadForumThreadTrackerManager()

    class Meta:
        unique_together = (('thread', 'user'),)
        verbose_name = _('Read forum thread tracker')
        verbose_name_plural = _('Read forum thread trackers')

    def save(self, *args, **kwargs):
        """
        Save the model.
        """

        # Set the last read date if not set
        if self.last_read_date is None:
            self.last_read_date = timezone.now()

        # Save the model
        super(ReadForumThreadTracker, self).save(*args, **kwargs)


class ForumUserProfile(models.Model):
    """
    Forum's user profile data model.
    """

    user = AutoOneToOneField(settings.AUTH_USER_MODEL,
                             related_name='forum_profile',
                             primary_key=True,
                             editable=False,
                             verbose_name=_('Related user'))

    notify_of_reply_by_default = models.BooleanField(_('Notify me of new reply by default'),
                                                     default=True)

    last_post_date = models.DateTimeField(_('Last post date'),
                                          default=None,
                                          blank=True,
                                          null=True)

    class Meta:
        verbose_name = _('Forum user profile')
        verbose_name_plural = _('Forum user profiles')

    def __str__(self):
        return 'Forum profile of "%s"' % self.user.username

    def is_flooding(self, now=None):
        """
        Returns ``True`` if the user has post something less than ``NB_SECONDS_BETWEEN_POSTS`` seconds from now.
        Returns ``False`` if the user has never post something.
        :param now: For testing purpose only.
        :return: bool ``True`` if the user is flooding (= trying to post two messages before the
        ``NB_SECONDS_BETWEEN_POSTS`` seconds delay is reached).
        """
        if self.last_post_date is None:
            return False
        if now is None:
            now = timezone.now()
        delta = now - self.last_post_date
        return delta.total_seconds() < NB_SECONDS_BETWEEN_POSTS

    def rearm_flooding_delay_and_save(self):
        """
        Re-arm the anti flood delay and save the model.
        """
        self.last_post_date = timezone.now()
        self.save(update_fields=('last_post_date', ))
