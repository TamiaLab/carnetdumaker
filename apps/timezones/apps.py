"""
Application file for the timezones app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TimezonesConfig(AppConfig):
    """
    Application configuration class for the timezones app.
    """

    name = 'apps.timezones'
    verbose_name = _('Timezones')
