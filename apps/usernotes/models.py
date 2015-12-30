"""
Data models for the user notes app.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class UserNote(models.Model):
    """
    User note model for administrators use only.
    An user note contain:
    - a title,
    - an author,
    - a description,
    - a target user,
    - a creation and modification dates,
    - a "sticky" flag.
    User notes MUST ONLY be used for administration purposes, like keeping trace of hack attempts, spam, flood, etc.
    Using this notes application for anything else may be illegal.
    """

    title = models.CharField(_('Title'),
                             max_length=255)

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='authored_admin_notes',
                               verbose_name=_('Author'))

    description = models.TextField(_('Description'))

    target_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    db_index=True,  # Database optimization
                                    related_name='admin_notes',
                                    verbose_name=_('Related user'))

    creation_date = models.DateTimeField(_('Creation date'),
                                         auto_now_add=True)

    last_modification_date = models.DateTimeField(_('Last modification date'),
                                                  auto_now=True)

    sticky = models.BooleanField(_('Sticky'),
                                 default=False)

    class Meta:
        verbose_name = _('User note')
        verbose_name_plural = _('User notes')
        get_latest_by = 'creation_date'
        ordering = ('-sticky', '-last_modification_date')

    def __str__(self):
        return self.title
