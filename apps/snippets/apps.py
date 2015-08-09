"""
Application file for the code snippets app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SnippetsConfig(AppConfig):
    """
    Application configuration class for the code snippets app.
    """

    name = 'apps.snippets'
    verbose_name = _('Code snippets')
