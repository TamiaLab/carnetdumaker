"""
Application file for the user API keys app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UserApiKeyConfig(AppConfig):
    """
    Application configuration class for the user API keys app.
    """

    name = 'apps.userapikey'
    verbose_name = _('User API keys')
