"""
Application file for the change email app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ChangeEmailConfig(AppConfig):
    """
    Application configuration class for the change email app.
    """

    name = 'apps.changemail'
    verbose_name = _('Change user email')
