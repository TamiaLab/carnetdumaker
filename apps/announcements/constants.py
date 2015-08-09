"""
Various constants and codes for the announcements app.
"""

from django.utils.translation import ugettext_lazy as _


ANNOUNCEMENTS_TYPE_DEFAULT = 'default'
ANNOUNCEMENTS_TYPE_SUCCESS = 'success'
ANNOUNCEMENTS_TYPE_INFO = 'info'
ANNOUNCEMENTS_TYPE_WARNING = 'warning'
ANNOUNCEMENTS_TYPE_DANGER = 'danger'
ANNOUNCEMENTS_TYPE_CHOICES = (
    (ANNOUNCEMENTS_TYPE_DEFAULT, _('Default')),
    (ANNOUNCEMENTS_TYPE_SUCCESS, _('Success')),
    (ANNOUNCEMENTS_TYPE_INFO, _('Information')),
    (ANNOUNCEMENTS_TYPE_WARNING, _('Warning')),
    (ANNOUNCEMENTS_TYPE_DANGER, _('Danger')),
)
