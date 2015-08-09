"""
Application file for the content report app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ContentReportConfig(AppConfig):
    """
    Application configuration class for the content report app.
    """

    name = 'apps.contentreport'
    verbose_name = _('User content report')
