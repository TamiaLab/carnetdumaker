"""
Application file for the static pages app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class StaticpagesConfig(AppConfig):
    """
    Application configuration class for the static pages app.
    """

    name = 'apps.staticpages'
    verbose_name = _('Static pages')
