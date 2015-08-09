"""
Application file for the anti-spam app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AntiSpamConfig(AppConfig):
    """
    Application configuration class for the anti-spam app.
    """

    name = 'apps.antispam'
    verbose_name = _('Anti-spam')
