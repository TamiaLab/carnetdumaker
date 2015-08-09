"""
Application file for the tools app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MiscToolsConfig(AppConfig):
    """
    Application configuration class for the tools app.
    """

    name = 'apps.tools'
    verbose_name = _('Misc. tools')
