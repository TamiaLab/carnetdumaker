"""
Objects managers for the announcements app.
"""

from django.db import models
from django.utils import timezone


class AnnouncementManager(models.Manager):
    """
    Manager class for the ``Announcement`` data model.
    """

    def published(self):
        """
        Return a queryset of all published announcements.
        """
        now = timezone.now()
        return self.filter(pub_date__isnull=False, pub_date__lte=now)

    def published_site_wide(self):
        """
        Return a queryset of all site wide announcements.
        """
        return self.published().filter(site_wide=True)
