"""
Application file for the file attachments app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FileAttachmentsConfig(AppConfig):
    """
    Application configuration class for the file attachments app.
    """

    name = 'apps.fileattachments'
    verbose_name = _('File attachments')
