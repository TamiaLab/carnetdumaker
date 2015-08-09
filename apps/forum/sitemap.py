"""
Sitemap for the forum app.
"""

from django.contrib.sitemaps import Sitemap

from .models import (Forum,
                     ForumThread)


class ForumsSitemap(Sitemap):
    """
    Sitemap for the forum.
    """

    changefreq = 'monthly'
    priority = 0.1

    def items(self):
        """
        Return all public forums.
        :return: All public forums.
        """
        return Forum.objects.public_forums()


class ForumThreadsSitemap(Sitemap):
    """
    Sitemap for the forum's thread.
    """

    changefreq = 'daily'
    priority = 0.5

    def items(self):
        """
        Return all public forum's threads.
        :return: All public forum's threads.
        """
        return ForumThread.objects.public_threads().select_related('last_post')

    def lastmod(self, obj):
        """
        Return the last modification date of the given forum's thread.
        :param obj: The forum's thread.
        :return: The last modification date of the given forum's thread.
        """
        return obj.last_post.last_modification_date
