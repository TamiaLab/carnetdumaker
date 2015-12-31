"""
Application file for the user strike app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UserStrikeConfig(AppConfig):
    """
    Application configuration class for the user strike app.
    """

    name = 'apps.userstrike'
    verbose_name = _('User strike')
