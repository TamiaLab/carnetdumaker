"""
Application file for the user registration app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RegistrationConfig(AppConfig):
    """
    Application configuration class for the user registration app.
    """

    name = 'apps.registration'
    verbose_name = _('User registration')
