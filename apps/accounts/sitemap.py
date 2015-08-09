"""
Sitemap for the user accounts app.
"""

from django.contrib.sitemaps import Sitemap
from django.contrib.auth import get_user_model


class AccountsSitemap(Sitemap):
    """
    Sitemap for all user accounts.
    """

    changefreq = 'weekly'
    priority = 0.1

    def items(self):
        """
        Return all active users.
        :return: All active users.
        """
        return get_user_model().objects.select_related('user_profile').filter(is_active=True)

    def location(self, obj):
        """
        Return the permalink to this user account.
        :param obj: The user object.
        :return: The permalink to the user account.
        """
        return obj.user_profile.get_absolute_url()

    def lastmod(self, obj):
        """
        Return the last modification date of the given user account.
        :param obj: The user object.
        :return: The last modification date of the given user account.
        """
        return obj.user_profile.last_modification_date
