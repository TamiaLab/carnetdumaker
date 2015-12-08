"""
Objects managers for the user accounts app.
"""

import datetime

from django.db import models
from django.utils import timezone

from .settings import ONLINE_USER_TIME_WINDOW_SECONDS


class UserProfileManager(models.Manager):
    """
    Manager class for the ``UserProfile`` data model.
    """

    def get_subscribers_for_newsletter(self):
        """
        Return a queryset of all user accounts who accept to receive the newsletter.
        """
        return self.filter(accept_newsletter=True)

    def get_online_users_accounts(self):
        """
        Return a queryset of all user accounts currently online.
        """
        offline_threshold = timezone.now() - datetime.timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS)
        return self.filter(online_status_public=True,
                           last_activity_date__isnull=False,
                           last_activity_date__gt=offline_threshold)

    def get_active_users_accounts(self):
        """
        Return a queryset of all active users.
        """
        return self.filter(user__is_active=True)
