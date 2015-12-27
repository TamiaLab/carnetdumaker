"""
Data models for the blog app.
"""

from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template import loader

from mptt.models import MPTTModel

from apps.tools.utils import unique_slug
from apps.tools.models import ModelDiffMixin
from apps.tools.fields import AutoResizingImageField
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_document
from apps.txtrender.signals import render_engine_changed
from apps.forum.models import (Forum,
                               ForumThread)
from apps.licenses.models import License
from apps.imageattachments.models import ImageAttachment

from .managers import ArticleManager
from .constants import (NOTE_TYPE_CHOICES,
                        NOTE_TYPE_DEFAULT,
                        ARTICLE_STATUS_CHOICES,
                        ARTICLE_STATUS_DRAFT,
                        ARTICLE_STATUS_DELETED,
                        ARTICLE_STATUS_PUBLISHED)
from .settings import (ARTICLE_HEADING_IMG_HEIGHT,
                       ARTICLE_HEADING_IMG_WIDTH,
                       ARTICLE_HEADING_UPLOAD_DIR_NAME,
                       ARTICLE_THUMBNAIL_IMG_HEIGHT,
                       ARTICLE_THUMBNAIL_IMG_WIDTH,
                       ARTICLE_THUMBNAIL_UPLOAD_DIR_NAME,
                       PARENT_FORUM_ID_FOR_ARTICLE_THREADS,
                       ARTICLE_CATEGORY_LOGO_UPLOAD_DIR_NAME,
                       ARTICLE_CATEGORY_LOGO_WIDTH,
                       ARTICLE_CATEGORY_LOGO_HEIGHT,
                       NB_DAYS_BEFORE_ARTICLE_GET_OLD)


class Article(ModelDiffMixin, models.Model):
    """
    Article main data model.
    An article is made of:
    - a slug, unique and database indexed,
    - a title and a subtitle (optional),
    - an optional brief description,
    - an author,
    - a status,
    - a license, auto set to null (default license) if the license is deleted,
    - a "network publish" flag, used by the "social publishing" feature,
    - a "featured" flag, for important news or article,
    - an optional heading image (full size and mobile version),
    - some creation, modification (content only) and publication dates,
    - an expiration date (for poll or time-limited article),
    - a "membership required" flag and flag expiration time (for paywall, can be set to null for time-unlimited),
    - a related forum thread for comments, auto set to null if deleted,
    - some tags, categories (warning: do not forget to add parent categories AND subcategories), image attachments,
    - some related and follow-up articles,
    - some head and foot notes,
    - some content (source and HTML),
    """

    # FIXME AutoSlugField
    slug = models.SlugField(_('Slug'),
                            max_length=255,
                            unique=True)

    title = models.CharField(_('Title'),
                             max_length=255)

    subtitle = models.CharField(_('Subtitle'),
                                max_length=255,
                                default='',
                                blank=True)

    description = RenderTextField(_('Description'))

    description_html = models.TextField(_('Description (raw HTML)'))

    description_text = models.TextField(_('Description (raw text)'))

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='authored_articles',
                               verbose_name=_('Author'))

    status = models.CharField(_('Status'),
                              db_index=True,  # Database optimization
                              max_length=10,
                              default=ARTICLE_STATUS_DRAFT,
                              choices=ARTICLE_STATUS_CHOICES)

    license = models.ForeignKey(License,
                                db_index=True,  # Database optimization
                                related_name='articles',
                                verbose_name=_('License'),
                                on_delete=models.SET_NULL,
                                default=None,
                                blank=True,
                                null=True)

    # If ``network_publish`` is true, the article will be published on social networks when it goes public.
    network_publish = models.BooleanField(_('Publish on other networks'),
                                          default=True)

    featured = models.BooleanField(_('Featured'),
                                   default=False)

    heading_img = AutoResizingImageField(_('Heading image'),
                                         upload_to=ARTICLE_HEADING_UPLOAD_DIR_NAME,
                                         height=ARTICLE_HEADING_IMG_HEIGHT,
                                         width=ARTICLE_HEADING_IMG_WIDTH,
                                         default=None,
                                         blank=True,
                                         null=True)

    thumbnail_img = AutoResizingImageField(_('Thumbnail image'),
                                           upload_to=ARTICLE_THUMBNAIL_UPLOAD_DIR_NAME,
                                           height=ARTICLE_THUMBNAIL_IMG_HEIGHT,
                                           width=ARTICLE_THUMBNAIL_IMG_WIDTH,
                                           default=None,
                                           blank=True,
                                           null=True)

    creation_date = models.DateTimeField(_('Creation date'),
                                         auto_now_add=True)

    last_content_modification_date = models.DateTimeField(_('Last content modification date'),
                                                          default=None,
                                                          blank=True,
                                                          null=True)

    pub_date = models.DateTimeField(_('Publication date'),
                                    db_index=True,  # Database optimization
                                    default=None,
                                    blank=True,
                                    null=True)

    expiration_date = models.DateTimeField(_('Expiration date'),
                                           db_index=True,  # Database optimization
                                           default=None,
                                           blank=True,
                                           null=True)

    membership_required = models.BooleanField(_('Membership required'),
                                              default=False)

    membership_required_expiration_date = models.DateTimeField(_('Membership required expiration date'),
                                                               default=None,
                                                               blank=True,
                                                               null=True)

    related_forum_thread = models.ForeignKey(ForumThread,
                                             related_name='+',
                                             verbose_name=_('Related forum thread'),
                                             default=None,
                                             null=True,
                                             blank=True,
                                             on_delete=models.SET_NULL)

    auto_create_related_forum_thread = models.BooleanField(_('Auto create related forum thread'),
                                                           default=True)

    tags = models.ManyToManyField('ArticleTag',
                                  related_name='articles',
                                  verbose_name=_('Article\'s tags'),
                                  blank=True)

    categories = models.ManyToManyField('ArticleCategory',
                                        related_name='articles',
                                        verbose_name=_('Article\'s categories'),
                                        blank=True)

    img_attachments = models.ManyToManyField(ImageAttachment,
                                             related_name='articles',
                                             verbose_name=_('Article\'s image attachments'),
                                             blank=True)

    display_img_gallery = models.BooleanField(_('Display the image gallery'),
                                              default=False)

    follow_up_of = models.ManyToManyField('Article',
                                          related_name='follow_up_articles',
                                          verbose_name=_('Follow up of'),
                                          blank=True)

    related_articles = models.ManyToManyField('Article',
                                              related_name='related_articles_reverse',
                                              verbose_name=_('Related articles'),
                                              blank=True)

    head_notes = models.ManyToManyField('ArticleNote',
                                        related_name='head_uses+',
                                        verbose_name=_('Article\'s heading notes'),
                                        blank=True)

    foot_notes = models.ManyToManyField('ArticleNote',
                                        related_name='foot_uses+',
                                        verbose_name=_('Article\'s footer notes'),
                                        blank=True)

    content = RenderTextField(_('Content'))

    content_html = models.TextField(_('Content (raw HTML)'))

    content_text = models.TextField(_('Content (raw text)'))

    summary_html = models.TextField(_('Summary (raw HTML)'))

    footnotes_html = models.TextField(_('Footnotes (raw HTML)'))

    objects = ArticleManager()

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        # NOTE Do NOT specify get_latest_by for this model because pub_date and creation_date have different meaning.
        ordering = ('-featured', '-creation_date')
        permissions = (('can_see_preview', 'Can see article in preview'),)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return the permalink to this article.
        """
        return reverse('blog:article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        All article saving logic happen here.
        Extra arguments:
        - current_user: The current editing user (None if not specified).
        - minor_change: If True the last modification date will not be changed.
        - revision_description: Revision description (optional).
        :param args: For super()
        :param kwargs: For super()
        """

        # Handle extra args
        current_user = kwargs.pop('current_user', None)
        minor_change = kwargs.pop('minor_change', False)
        revision_description = kwargs.pop('revision_description', '')

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(Article, self, self.slug, 'slug', self.title)

        # Get all dirty fields
        changed_fields = self.diff

        # Handle pub_date
        now = timezone.now()
        if self.status == ARTICLE_STATUS_PUBLISHED and self.pub_date is None:
            self.pub_date = now
            self.last_content_modification_date = None

        # Update last content modification date if necessary
        elif self.pk and ('title' in changed_fields or
                                  'subtitle' in changed_fields or
                                  'description' in changed_fields or
                                        'content' in changed_fields):
            self.last_content_modification_date = now

        # Fix last content modification date if necessary
        if self.last_content_modification_date is not None \
                and self.pub_date is not None \
                and self.last_content_modification_date <= self.pub_date:
            self.last_content_modification_date = None
        elif self.pub_date is None:
            self.last_content_modification_date = None

        # Render HTML content
        self.render_text()

        # Save the model
        super(Article, self).save(*args, **kwargs)

        # Auto create related forum thread if required
        if self.status == ARTICLE_STATUS_PUBLISHED \
                and self.auto_create_related_forum_thread \
                and self.related_forum_thread is None:
            self.create_related_forum_thread()

        # Detect article change
        if self.pk and ('title' in changed_fields or
                                'subtitle' in changed_fields or
                                'description' in changed_fields or
                                'content' in changed_fields):
            old_title = changed_fields['title'][0] if 'title' in changed_fields else self.title
            old_subtitle = changed_fields['subtitle'][0] if 'subtitle' in changed_fields else self.subtitle
            old_description = changed_fields['description'][0] if 'description' in changed_fields else self.description
            old_content = changed_fields['content'][0] if 'content' in changed_fields else self.content
            ArticleRevision.objects.create(related_article=self,
                                           revision_minor_change=minor_change,
                                           revision_description=revision_description,
                                           revision_author=current_user,
                                           title=old_title,
                                           subtitle=old_subtitle,
                                           description=old_description,
                                           content=old_content)

    def create_related_forum_thread(self,
                                    template_name='blog/auto_forum_post_body.html',
                                    extra_context=None):
        """
        Create the related forum thread and first post. Does not save the model after that.
        :param template_name: The template name to be used to generate the first post body text.
        :param extra_context: Any extra context for the template.
        """

        # Do nothing if parent forum ID is not set
        if PARENT_FORUM_ID_FOR_ARTICLE_THREADS is None:
            return

        # Get the forum instance
        try:
            parent_forum_obj = Forum.objects.get(pk=PARENT_FORUM_ID_FOR_ARTICLE_THREADS)
        except Forum.DoesNotExist:
            raise ImproperlyConfigured('PARENT_FORUM_ID_FOR_ARTICLE_THREADS is set to a non-existing forum PK.')

        # Render the first post using the given template
        context = {
            'article': self,
        }
        if extra_context:
            context.update(extra_context)
        post_body_html = loader.render_to_string(template_name, context)

        # Create the related forum thread
        self.related_forum_thread = ForumThread.objects.create_thread(parent_forum=parent_forum_obj,
                                                                      title=self.title,
                                                                      author=self.author,
                                                                      pub_date=self.pub_date,
                                                                      content=post_body_html,
                                                                      author_ip_address=None)

    def require_membership_for_reading(self):
        """
        Return ``True`` if the user need membership to read the article, ``False`` otherwise.
        """
        now = timezone.now()
        if self.membership_required_expiration_date is None:
            return self.membership_required
        return self.membership_required and now <= self.membership_required_expiration_date
    require_membership_for_reading.boolean = True
    require_membership_for_reading.short_description = _('Require membership for reading')

    def is_published(self):
        """
        Return ``True`` if this article is published and so, readable by anyone.
        Note: check if gone before checking if published to handle HTTP 410 code.
        """
        now = timezone.now()
        return self.status == ARTICLE_STATUS_PUBLISHED and \
               now >= self.pub_date and \
               (now <= self.expiration_date if self.expiration_date else True)
    is_published.boolean = True
    is_published.short_description = _('Published')

    def is_gone(self):
        """
        Return ``True`` if this article is gone (not accessible anymore).
        """
        now = timezone.now()
        return self.status == ARTICLE_STATUS_DELETED or \
               (now > self.expiration_date if self.expiration_date else False)
    is_gone.boolean = True
    is_gone.short_description = _('Deleted')

    def is_old(self):
        """
        Return ``True`` if the last modification date or publication date
        is older than ``NB_DAYS_BEFORE_ARTICLE_GET_OLD`` days.
        """
        last_update_date = self.last_content_modification_date or self.pub_date
        old_threshold_date = timezone.now() - timedelta(days=NB_DAYS_BEFORE_ARTICLE_GET_OLD)
        return last_update_date < old_threshold_date
    is_old.boolean = True
    is_old.short_description = _('Old')

    def can_see_preview(self, user):
        """
        Return True if the given user can see this article in preview mode.
        :param user: The user to be checked for permission
        """
        return user == self.author or user.has_perm('blog.can_see_preview')

    def has_been_modified_after_publication(self):
        """
        Return True if the article has been modified after publication.
        """
        return self.last_content_modification_date is not None and \
               self.last_content_modification_date != self.pub_date

    def render_text(self, save=False):
        """
        Render the content. Save the model only if ``save`` is True.
        """

        # Render HTML for description
        description_html, description_text, _ = render_document(self.description,
                                                                allow_text_formating=True,
                                                                allow_text_extra=True,
                                                                allow_text_alignments=True,
                                                                allow_text_directions=True,
                                                                allow_text_modifiers=True,
                                                                allow_text_colors=True,
                                                                allow_acronyms=True,
                                                                allow_links=True,
                                                                allow_cdm_extra=True,
                                                                force_nofollow=False,
                                                                render_text_version=True)
        self.description_html = description_html
        self.description_text = description_text

        # Render HTML for content
        content_html, content_text, extra_dict = render_document(self.content,
                                                                 allow_titles=True,
                                                                 allow_code_blocks=True,
                                                                 allow_text_formating=True,
                                                                 allow_text_extra=True,
                                                                 allow_text_alignments=True,
                                                                 allow_text_directions=True,
                                                                 allow_text_modifiers=True,
                                                                 allow_text_colors=True,
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
                                                                 allow_cdm_extra=True,
                                                                 force_nofollow=False,
                                                                 render_text_version=True,
                                                                 render_extra_dict=True,
                                                                 merge_footnotes_text=True)
        self.content_html = content_html
        self.content_text = content_text
        self.summary_html = extra_dict['summary_html']
        self.footnotes_html = extra_dict['footnotes_html']

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(Article, self).save(update_fields=('description_html', 'description_text',
                                                     'content_html', 'content_text',
                                                     'summary_html', 'footnotes_html'))


def _redo_articles_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all articles.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for article in Article.objects.all():
        article.render_text(save=True)

render_engine_changed.connect(_redo_articles_text_rendering)


class ArticleRevision(models.Model):
    """
    Article's revision data model.
    An article's revision is made of:
    - a related article. Revisions of a specific article are available through the ``revisions`` attribute of the
    given ``Article`` class.
    - the old title, subtitle, description and content of the related article,
    - a brief description (optional),
    - a "minor change" flag,
    - a revision date and an author (can be null).
    """

    related_article = models.ForeignKey(Article,
                                        db_index=True,  # Database optimization
                                        editable=False,
                                        related_name='revisions',
                                        verbose_name=_('Related article'))

    title = models.CharField(_('Title'),
                             editable=False,
                             max_length=255)

    subtitle = models.CharField(_('Subtitle'),
                                editable=False,
                                max_length=255,
                                default='',
                                blank=True)

    description = models.TextField(_('Description'),
                                   editable=False,
                                   default='',
                                   blank=True)

    content = models.TextField(_('Content'),
                               editable=False)

    revision_minor_change = models.BooleanField(_('Minor changes'),
                                                editable=False,
                                                default=False)

    revision_description = models.TextField(_('Revision description'),
                                            editable=False,
                                            default='',
                                            blank=True)

    revision_author = models.ForeignKey(settings.AUTH_USER_MODEL,
                                        editable=False,
                                        related_name='+',
                                        verbose_name=_('Revision author'),
                                        default=None,
                                        blank=True,
                                        null=True)

    revision_date = models.DateTimeField(_('Revision date'),
                                         auto_now_add=True)

    class Meta:
        verbose_name = _('Article revision')
        verbose_name_plural = _('Article revisions')
        get_latest_by = 'revision_date'
        ordering = ('-revision_date',)

    def __str__(self):
        return 'Revision #%d' % self.id


class ArticleNote(models.Model):
    """
    Article's note data model.
    An article's note is made of:
    - a title (one mandatory for internal use only, and one optional for display),
    - a description (source and html version),
    - a type for display.
    """

    title_internal = models.CharField(_('Title (for internal use)'),
                                      max_length=255)

    title = models.CharField(_('Title'),
                             max_length=255,
                             default='',
                             blank=True)

    description = RenderTextField(_('Description'))

    description_html = models.TextField(_('Description (raw HTML)'))

    type = models.CharField(_('Note type'),
                            max_length=10,
                            default=NOTE_TYPE_DEFAULT,
                            choices=NOTE_TYPE_CHOICES)

    class Meta:
        verbose_name = _('Article note')
        verbose_name_plural = _('Article notes')

    def __str__(self):
        return self.title_internal

    def save(self, *args, **kwargs):
        """
        Save the model
        :param args: For super()
        :param kwargs: For super()
        """

        # Render the description text
        self.render_description()

        # Save the note
        super(ArticleNote, self).save(*args, **kwargs)

    def render_description(self, save=False):
        """
        Render the description. Save the model only if ``save`` is True.
        """

        # Render HTML
        content_html, content_text, _ = render_document(self.description,
                                                        allow_code_blocks=True,
                                                        allow_text_formating=True,
                                                        allow_text_extra=True,
                                                        allow_text_alignments=True,
                                                        allow_text_directions=True,
                                                        allow_text_modifiers=True,
                                                        allow_text_colors=True,
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
                                                        allow_cdm_extra=True,
                                                        force_nofollow=False)
        self.description_html = content_html

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(ArticleNote, self).save(update_fields=('description_html', ))


def _redo_article_notes_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all article's notes.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for note in ArticleNote.objects.all():
        note.render_description(save=True)

render_engine_changed.connect(_redo_article_notes_text_rendering)


class ArticleTag(models.Model):
    """
    Article's tag data model.
    An article's tag is made of:
    - a slug (unique and indexed in database),
    - a name (human readable).
    """

    # FIXME AutoSlugField
    slug = models.SlugField(_('Slug'),
                            max_length=255,
                            unique=True)

    name = models.CharField(_('Name'),
                            max_length=255)

    class Meta:
        verbose_name = _('Article tag')
        verbose_name_plural = _('Article tags')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Return the permalink to this article's tag.
        """
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})

    def get_latest_articles_rss_feed_url(self):
        """
        Return the permalink to "latest articles" RSS feed for this tag.
        """
        return reverse('blog:latest_tag_articles_rss', kwargs={'slug': self.slug})

    def get_latest_articles_atom_feed_url(self):
        """
        Return the permalink to "latest articles" Atom feed for this tag.
        """
        return reverse('blog:latest_tag_articles_atom', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Save the model
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(ArticleTag, self, self.slug, 'slug', self.name)

        # Save the tag
        super(ArticleTag, self).save(*args, **kwargs)


class ArticleCategory(MPTTModel):
    """
    Article's category data model.
    An article's category is made of:
    - a parent category, can be null for a root category. The child categories of a category are available using
    the ``children`` attribute of the parent category.
    - a slug, the slug itself is NOT unique. However, the slug and the parent slugs ARE unique together.
    Sub-category slug are made using recursive URL patterns.
    - a precomputed slug hierarchy, for fast object access in database.
    - a name (human readable),
    - an optional description (text only).
    """

    parent = models.ForeignKey('self',
                               db_index=True,  # Database optimization
                               related_name='children',
                               verbose_name=_('Parent category'),
                               default=None,
                               blank=True,
                               null=True)

    # FIXME AutoSlugField
    slug = models.SlugField(_('Slug'),
                            max_length=255)

    slug_hierarchy = models.SlugField(_('Slug hierarchy'),
                                      max_length=1023,
                                      unique=True)

    name = models.CharField(_('Name'),
                            max_length=255)

    logo = AutoResizingImageField(_('Logo'),
                                  upload_to=ARTICLE_CATEGORY_LOGO_UPLOAD_DIR_NAME,
                                  width=ARTICLE_CATEGORY_LOGO_WIDTH,
                                  height=ARTICLE_CATEGORY_LOGO_HEIGHT,
                                  default=None,
                                  blank=True,
                                  null=True)

    description = RenderTextField(_('Description'))

    description_html = models.TextField(_('Description (raw HTML)'))

    description_text = models.TextField(_('Description (raw text)'))

    class Meta:
        unique_together = (('slug', 'parent'),)
        verbose_name = _('Article category')
        verbose_name_plural = _('Article categories')

    def save(self, *args, **kwargs):
        """
        Save the model
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(ArticleCategory, self, self.slug, 'slug', self.name, {'parent': self.parent})

        # Build complete slug hierarchy
        self.build_slug_hierarchy()

        # Render the description
        self.render_text()

        # Save the category
        super(ArticleCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Return the permalink to this category.
        """
        return reverse('blog:category_detail', kwargs={'hierarchy': self.slug_hierarchy})

    def get_latest_articles_rss_feed_url(self):
        """
        Return the permalink to "latest articles" RSS feed for this category.
        """
        return reverse('blog:latest_category_articles_rss', kwargs={'hierarchy': self.slug_hierarchy})

    def get_latest_articles_atom_feed_url(self):
        """
        Return the permalink to "latest articles" Atom feed for this category.
        """
        return reverse('blog:latest_category_articles_atom', kwargs={'hierarchy': self.slug_hierarchy})

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
            super(ArticleCategory, self).save(update_fields=('slug_hierarchy',
                                                             'parent',
                                                             'level',
                                                             'lft',
                                                             'rght',
                                                             'tree_id'))

    def render_text(self, save=False):
        """
        Render the content. Save the model only if ``save`` is True.
        """

        # Render HTML for description
        description_html, description_text, _ = render_document(self.description,
                                                                allow_text_formating=True,
                                                                allow_text_extra=True,
                                                                allow_text_alignments=True,
                                                                allow_text_directions=True,
                                                                allow_text_modifiers=True,
                                                                allow_text_colors=True,
                                                                allow_acronyms=True,
                                                                allow_links=True,
                                                                allow_cdm_extra=True,
                                                                force_nofollow=False,
                                                                render_text_version=True)
        self.description_html = description_html
        self.description_text = description_text

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(ArticleCategory, self).save(update_fields=('description_html', 'description_text'))


def _redo_article_categories_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all article categories.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for category in ArticleCategory.objects.all():
        category.render_text(save=True)

render_engine_changed.connect(_redo_article_categories_text_rendering)


def update_child_category_slug_hierarchy_on_parent_save(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    Update any children category's slug hierarchy on parent save.
    :param sender: The ArticleCategory class.
    :param instance: The category instance.
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

    # Update child categories
    for child in instance.children.all():
        child.build_slug_hierarchy(save=True)

post_save.connect(update_child_category_slug_hierarchy_on_parent_save, sender=ArticleCategory)
