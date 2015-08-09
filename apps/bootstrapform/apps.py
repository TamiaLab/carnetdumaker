"""
Application file for the bootstrap forms app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BootstrapFormsConfig(AppConfig):
    """
    Application configuration class for the bootstrap forms app.
    """

    name = 'apps.bootstrapform'
    verbose_name = _('Bootstrap forms')
