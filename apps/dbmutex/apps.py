"""
Application file for the database mutex app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DatabaseMutexConfig(AppConfig):
    """
    Application configuration class for the database mutex app.
    """

    name = 'apps.dbmutex'
    verbose_name = _('Mutex locks')
