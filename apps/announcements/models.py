"""
Data models for the announcements app.
"""

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from apps.tools.utils import unique_slug
from apps.tools.models import ModelDiffMixin
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_html, strip_html
from apps.txtrender.signals import render_engine_changed

from .managers import AnnouncementManager
from .constants import (ANNOUNCEMENTS_TYPE_CHOICES,
                        ANNOUNCEMENTS_TYPE_DEFAULT)


class Announcement(ModelDiffMixin, models.Model):
    """
    Announcement data model. Use to quickly broadcast information about the site.
    An announcement is made of:
    - a title,
    - a slug (unique and indexed),
    - an author,
    - a publication date,
    - a type,
    - a "site wide" flag, used to determine if the announcement should be displayed on the front page.
    - some text (source and HTML version).
    """

    title = models.CharField(_('Title'),
                             max_length=255)

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

    objects = AnnouncementManager()

    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        permissions = (('can_see_preview', 'Can see any announcements in preview'),)
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
        All article saving logic happen here.
        :param args: For super()
        :param kwargs: For super()
        """

        # Avoid duplicate slug
        self.slug = unique_slug(Announcement, self, self.slug, 'slug', self.title)

        # Fix the modification date if necessary
        changed_fields = self.changed_fields
        if 'title' in changed_fields or 'content' in changed_fields:
            self.last_content_modification_date = timezone.now()
        if self.pub_date and self.last_content_modification_date \
                and self.last_content_modification_date < self.pub_date:
            self.last_content_modification_date = self.pub_date

        # Render the content
        self.render_text()

        # Save the model
        super(Announcement, self).save(*args, **kwargs)

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
        Return True if the given user can see this article in preview mode.
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
        self.content_html = render_html(self.content, force_nofollow=False)

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(Announcement, self).save(update_fields=('content_html',))

    @cached_property
    def get_content_without_html(self):
        """
        Return the announcement's text without any HTML tag nor entities.
        """
        return strip_html(self.content_html)


def _redo_announcements_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all announcements.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for announcement in Announcement.objects.all():
        announcement.render_text(save=True)


render_engine_changed.connect(_redo_announcements_text_rendering)
