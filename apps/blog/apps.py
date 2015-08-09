"""
Application file for the blog app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BlogConfig(AppConfig):
    """
    Application configuration class for the blog app.
    """

    name = 'apps.blog'
    verbose_name = _('Articles')
