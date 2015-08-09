"""
Application file for the licenses app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LicensesConfig(AppConfig):
    """
    Application configuration class for the licenses app.
    """

    name = 'apps.licenses'
    verbose_name = _('Licenses')
