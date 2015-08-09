"""
Application file for the countries app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CountriesConfig(AppConfig):
    """
    Application configuration class for the countries app.
    """

    name = 'apps.countries'
    verbose_name = _('Countries')
