"""
Application file for the text rendering app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TextRenderConfig(AppConfig):
    """
    Application configuration class for the text rendering app.
    """

    name = 'apps.txtrender'
    verbose_name = _('Text rendering')
