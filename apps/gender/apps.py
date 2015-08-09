"""
Application file for the gender app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GenderConfig(AppConfig):
    """
    Application configuration class for the gender app.
    """

    name = 'apps.gender'
    verbose_name = _('Gender')
