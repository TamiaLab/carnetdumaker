"""
Application file for the image attachments app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ImageAttachmentsConfig(AppConfig):
    """
    Application configuration class for the image attachments app.
    """

    name = 'apps.imageattachments'
    verbose_name = _('Image attachments')
