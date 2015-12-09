"""
Objects managers for the announcements app.
"""

from django.db import models
from django.utils import timezone

from .utils import publish_announcement_on_twitter


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


class AnnouncementTwitterCrossPublicationManager(models.Manager):
    """
    Manager class for the ``Announcement`` data model.
    """

    def publish_pending_announcements(self):
        """
        Publish on Twitter any announcements published on the site but not yet on Twitter.
        """
        from .models import Announcement

        # Get all unpublished announcements
        announcements_unpublished = Announcement.objects.published().filter(twitter_pubs__isnull=True)

        # Publish all announcements
        for announcement in announcements_unpublished:

            # Publish on Twitter
            tweet_id = publish_announcement_on_twitter(announcement)

            # Handle success
            if tweet_id:

                # Mark announcement as published on Twitter
                self.create(announcement=announcement, tweet_id=tweet_id)
