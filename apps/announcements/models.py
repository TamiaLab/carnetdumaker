"""
Data models for the announcements app.
"""

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.tools.utils import unique_slug
from apps.tools.models import ModelDiffMixin
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_document
from apps.txtrender.signals import render_engine_changed

from .managers import (AnnouncementManager,
                       AnnouncementTwitterCrossPublicationManager)
from .constants import (ANNOUNCEMENTS_TYPE_CHOICES,
                        ANNOUNCEMENTS_TYPE_DEFAULT)


class Announcement(ModelDiffMixin, models.Model):
    """
    Announcement data model. Use to quickly broadcast information about the site.
    An announcement is made of:
    - a title,
    - a slug (unique and indexed),
    - an author,
    - a creation, last content modification and publication date,
    - a type,
    - a "site wide" flag, used to determine if the announcement should be displayed on the front page.
    - some text (source and HTML version).
    Announcements made by a specific user are available using the reverse relation ``authored_announcements``.
    """

    title = models.CharField(_('Title'),
                             max_length=255)

    # FIXME AutoSlugField
    slug = models.SlugField(_('Slug'),
                            max_length=255,
                            unique=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='authored_announcements',
                               verbose_name=_('Author'))

    creation_date = models.DateTimeField(_('Creation date'),
                                         auto_now_add=True,
                                         db_index=True)  # Database optimization

    last_content_modification_date = models.DateTimeField(_('Last content modification date'),
                                                          default=None,
                                                          editable=False,
                                                          blank=True,
                                                          null=True,
                                                          db_index=True)  # Database optimization

    pub_date = models.DateTimeField(_('Publication date'),
                                    default=None,
                                    blank=True,
                                    null=True,
                                    db_index=True)  # Database optimization

    type = models.CharField(_('Type'),
                            max_length=10,
                            choices=ANNOUNCEMENTS_TYPE_CHOICES,
                            default=ANNOUNCEMENTS_TYPE_DEFAULT)

    site_wide = models.BooleanField(_('Broadcast all over the site'),
                                    default=False)

    content = RenderTextField(_('Content'))

    content_html = models.TextField(_('Content (raw HTML)'))

    content_text = models.TextField(_('Content (raw text)'))

    tags = models.ManyToManyField('AnnouncementTag',
                                  related_name='announcements',
                                  verbose_name=_('Announcement\'s tags'),
                                  blank=True)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    objects = AnnouncementManager()

    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        permissions = (
            ('can_see_preview', 'Can see any announcements in preview'),
        )
        get_latest_by = 'pub_date'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Return the permalink to this announcement.
        """
        return reverse('announcements:announcement_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Save the announcement, fix non-unique slug, fix/update last content modification date and render the text.
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(Announcement, self, self.slug, 'slug', self.title)

        # Fix the modification date if necessary
        self.fix_last_content_modification_date()

        # Render the content
        self.render_text()

        # Save the model
        super(Announcement, self).save(*args, **kwargs)

    def save_no_rendering(self, *args, **kwargs):
        """
        Save the announcement without doing any text rendering or fields cleanup.
        This method just call the parent ``save`` method.
        :param args: For super()
        :param kwargs: For super()
        """
        super(Announcement, self).save(*args, **kwargs)

    def fix_last_content_modification_date(self):
        """
        Fix the ``last_content_modification_date`` field according to ``pub_date`` and other fields.
        """
        if self.pub_date:
            changed_fields = self.changed_fields
            if self.pk and 'title' in changed_fields or 'content' in changed_fields:
                self.last_content_modification_date = timezone.now()

            if self.last_content_modification_date \
                    and self.last_content_modification_date <= self.pub_date:
                self.last_content_modification_date = None
        else:
            self.last_content_modification_date = None

    def is_published(self):
        """
        Return ``True`` if this announcement is published and so, readable by anyone.
        """
        now = timezone.now()
        return self.pub_date is not None and self.pub_date <= now
    is_published.boolean = True
    is_published.short_description = _('Published')

    def can_see_preview(self, user):
        """
        Return True if the given user can see this announcement in preview mode.
        :param user: The user to be checked for permission
        """
        return user == self.author or user.has_perm('announcements.can_see_preview')

    def has_been_modified_after_publication(self):
        """
        Return True if the announcement has been modified after publication.
        """
        return self.last_content_modification_date is not None \
               and self.last_content_modification_date != self.pub_date

    def render_text(self, save=False):
        """
        Render the content.
        :param save: Save the model field ``content_html`` if ``True``.
        """

        # Render HTML
        content_html, content_text, _ = render_document(self.content,
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
                                                        merge_footnotes_html=True,
                                                        merge_footnotes_text=True)
        self.content_html = content_html
        self.content_text = content_text

        # Save if required
        if save:
            self.save_no_rendering(update_fields=('content_html', 'content_text'))


def _redo_announcements_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all announcements.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for announcement in Announcement.objects.all():
        announcement.render_text(save=True)

render_engine_changed.connect(_redo_announcements_text_rendering)


class AnnouncementTag(models.Model):
    """
    Announcement tag data model.
    An announcement's tag is made of:
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
        verbose_name = _('Announcement tag')
        verbose_name_plural = _('Announcement tags')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Return the permalink to this announcement's tag.
        """
        return reverse('announcements:tag_detail', kwargs={'slug': self.slug})

    def get_latest_announcements_rss_feed_url(self):
        """
        Return the permalink to "latest announcements" RSS feed for this tag.
        """
        return reverse('announcements:latest_tag_announcements_rss', kwargs={'slug': self.slug})

    def get_latest_announcements_atom_feed_url(self):
        """
        Return the permalink to "latest announcements" Atom feed for this tag.
        """
        return reverse('announcements:latest_tag_announcements_atom', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Save the model
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        # FIXME AutoSlugField
        self.slug = unique_slug(AnnouncementTag, self, self.slug, 'slug', self.name)

        # Save the tag
        super(AnnouncementTag, self).save(*args, **kwargs)


class AnnouncementTwitterCrossPublication(models.Model):
    """
    Cross-publication marker for the Twitter platform.
    This simple model store three information:
    - the cross-published announcement,
    - the tweet ID of the cross-publication (for history in case of problem),
    - the date of cross-publication.
    """

    announcement = models.ForeignKey('Announcement',
                                     db_index=True,  # Database optimization
                                     related_name='twitter_pubs',
                                     verbose_name=_('Announcement'))

    tweet_id = models.CharField(_('Tweet ID'),
                                db_index=True,  # Database optimization
                                max_length=255)

    pub_date = models.DateTimeField(_('Creation date'),
                                    auto_now_add=True,
                                    db_index=True)  # Database optimization

    objects = AnnouncementTwitterCrossPublicationManager()

    class Meta:
        verbose_name = _('Twitter cross-publication')
        verbose_name_plural = _('Twitter cross-publications')
        get_latest_by = 'pub_date'
        ordering = ('-pub_date', )

    def __str__(self):
        return '%s -> %s' % (self.announcement, self.tweet_id)
