"""
Application file for the home pages app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class HomePagesConfig(AppConfig):
    """
    Application configuration class for the home pages app.
    """

    name = 'apps.home'
    verbose_name = _('Home pages')
