"""
Application file for the user notes app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UserNotesConfig(AppConfig):
    """
    Application configuration class for the user notes app.
    """

    name = 'apps.usernotes'
    verbose_name = _('User notes')
