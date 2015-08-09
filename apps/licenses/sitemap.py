"""
Sitemap for the licenses app.
"""

from django.contrib.sitemaps import Sitemap

from .models import License


class LicensesSitemap(Sitemap):
    """
    Sitemap for the licenses.
    """

    changefreq = 'monthly'
    priority = 0.2

    def items(self):
        """
        Return all licenses.
        :return: All licenses.
        """
        return License.objects.all()

    def lastmod(self, obj):
        """
        Return the last modification date of the given license.
        :param obj: The license.
        :return: The last modification date of the given license.
        """
        return obj.last_modification_date
