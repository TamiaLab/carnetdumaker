"""
Application file for the user accounts app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountsConfig(AppConfig):
    """
    Application configuration class for the user accounts app.
    """

    name = 'apps.accounts'
    verbose_name = _('User profiles')
