"""
Application file for the log watcher app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LogWatcherConfig(AppConfig):
    """
    Application configuration class for the log watcher app.
    """

    name = 'apps.loginwatcher'
    verbose_name = _('Log watcher')
