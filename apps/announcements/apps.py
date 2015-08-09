"""
Application file for the announcements app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AnnouncementsConfig(AppConfig):
    """
    Application configuration class for the announcements app.
    """

    name = 'apps.announcements'
    verbose_name = _('Announcements')
