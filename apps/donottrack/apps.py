"""
Application file for the DoNotTrack app.
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DoNotTrackConfig(AppConfig):
    """
    Application configuration class for the DoNotTrack app.
    """

    name = 'apps.donottrack'
    verbose_name = _('DoNotTrack support')
