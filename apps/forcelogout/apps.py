"""
Application file for the force logout app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ForceLogoutConfig(AppConfig):
    """
    Application configuration class for the force logout app.
    """

    name = 'apps.forcelogout'
    verbose_name = _('Force logout')
