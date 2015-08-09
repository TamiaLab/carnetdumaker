"""
Objects managers for the user accounts app.
"""

from django.db import models


class UserProfileManager(models.Manager):
    """
    Manager class for the ``UserProfile`` data model.
    """

    def get_subscribers_for_newsletter(self):
        """
        Return a queryset of all users accepting to receive the newsletter.
        """
        return self.filter(accept_newsletter=True)
