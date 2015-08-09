"""
Application file for the pagination app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PaginatorConfig(AppConfig):
    """
    Application configuration class for the pagination app.
    """

    name = 'apps.paginator'
    verbose_name = _('Paginator')
