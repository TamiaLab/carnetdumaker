"""
Application file for the private messages app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PrivateMsgConfig(AppConfig):
    """
    Application configuration class for the private messages app.
    """

    name = 'apps.privatemsg'
    verbose_name = _('Private messages')
