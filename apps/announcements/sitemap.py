"""
Sitemap for the announcements app.
"""

from django.contrib.sitemaps import Sitemap

from .models import (Announcement,
                     AnnouncementTag)


class AnnouncementsSitemap(Sitemap):
    """
    Sitemap for the announcements.
    """

    changefreq = 'daily'
    priority = 0.4

    def items(self):
        """
        Return all published announcements.
        :return: All published announcements.
        """
        return Announcement.objects.published()

    def lastmod(self, obj):
        """
        Return the last modification date of the given announcement.
        :param obj: The announcement.
        :return: The last modification date of the given announcement.
        """
        return obj.last_content_modification_date or obj.pub_date


class AnnouncementTagsSitemap(Sitemap):
    """
    Sitemap for the announcement tags.
    """

    changefreq = 'weekly'
    priority = 0.1

    def items(self):
        """
        Return all announcement tags.
        :return: All announcement tags.
        """
        return AnnouncementTag.objects.all()
