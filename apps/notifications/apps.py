"""
Application file for the notifications app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class NotificationsConfig(AppConfig):
    """
    Application configuration class for the notifications app.
    """

    name = 'apps.notifications'
    verbose_name = _('Notifications')
