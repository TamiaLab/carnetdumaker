"""
Application file for the multi-upload form field app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MultiuploadConfig(AppConfig):
    """
    Application configuration class for the multi-upload form field app.
    """

    name = 'apps.multiupload'
    verbose_name = _('Multi-upload form field')
