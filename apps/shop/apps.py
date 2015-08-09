"""
Application file for the e-commerce app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ShopConfig(AppConfig):
    """
    Application configuration class for the e-commerce app.
    """

    name = 'apps.shop'
    verbose_name = _('E-commerce')
