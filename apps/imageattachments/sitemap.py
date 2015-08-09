"""
Sitemap for the image attachments app.
"""

from django.contrib.sitemaps import Sitemap

from .models import ImageAttachment


class ImageAttachmentsSitemap(Sitemap):
    """
    Sitemap for the image attachments.
    """

    changefreq = 'daily'
    priority = 0.4

    def items(self):
        """
        Return all the published image attachments.
        :return: All the published image attachments.
        """
        return ImageAttachment.objects.published()

    def lastmod(self, obj):
        """
        Return the last modification date of the given image attachment.
        :param obj: The image attachment.
        :return: The last modification date of the given image attachment.
        """
        return obj.pub_date
