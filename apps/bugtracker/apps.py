"""
Application file for the bug tracker app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BugtrackerConfig(AppConfig):
    """
    Application configuration class for the bug tracker app.
    """

    name = 'apps.bugtracker'
    verbose_name = _('Bug tracker')
