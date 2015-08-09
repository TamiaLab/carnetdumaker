"""
Application file for the forum app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ForumConfig(AppConfig):
    """
    Application configuration class for the forum app.
    """

    name = 'apps.forum'
    verbose_name = _('Forum')
