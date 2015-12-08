"""
Sitemap for the user accounts app.
"""

from django.contrib.sitemaps import Sitemap

from .models import UserProfile


class AccountsSitemap(Sitemap):
    """
    Sitemap for all user accounts.
    """

    changefreq = 'weekly'
    priority = 0.1

    def items(self):
        """
        Return all active user accounts.
        :return: All active user accounts.
        """
        return UserProfile.objects.get_active_users_accounts()

    def location(self, obj):
        """
        Return the permalink to this user account.
        :param obj: The user object.
        :return: The permalink to the user account.
        """
        return obj.get_absolute_url()

    def lastmod(self, obj):
        """
        Return the last modification date of the given user account.
        :param obj: The user object.
        :return: The last modification date of the given user account.
        """
        return obj.last_modification_date
