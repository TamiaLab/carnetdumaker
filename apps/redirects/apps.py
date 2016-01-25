"""
Application file for the redirect app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RedirectsConfig(AppConfig):
    """
    Application configuration class for the redirect app.
    """

    name = 'apps.redirects'
    verbose_name = _('Redirects')
