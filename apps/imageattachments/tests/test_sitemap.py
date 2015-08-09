"""
Tests suite for the sitemap of the image attachments app.
"""

from django.test import TestCase

from ..models import ImageAttachment
from ..sitemap import ImageAttachmentsSitemap


class ImageAttachmentsSitemapTestCase(TestCase):
    """
    Tests suite for the ``ImageAttachmentsSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        ImageAttachment.objects.create(title='Test 1',
                                       slug='test-1',
                                       img_original='fixtures/mea.jpg')
        ImageAttachment.objects.create(title='Test 2',
                                       slug='test-2',
                                       img_original='fixtures/mea.jpg')
        ImageAttachment.objects.create(title='Test 3',
                                       slug='test-3',
                                       img_original='fixtures/mea.jpg')

        # Test the resulting sitemap content
        sitemap = ImageAttachmentsSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<ImageAttachment: Test 3>',
                                         '<ImageAttachment: Test 2>',
                                         '<ImageAttachment: Test 1>'])

    def test_lastmod(self):
        """
        Test the ``lastmod`` method of the sitemap with an announcement modified after being published.
        """

        # Create some test fixtures
        image = ImageAttachment.objects.create(title='Test 1',
                                               slug='test-1',
                                               img_original='fixtures/mea.jpg')
        self.assertIsNotNone(image.pub_date)

        # Test the result of the method
        sitemap = ImageAttachmentsSitemap()
        self.assertEqual(sitemap.lastmod(image), image.pub_date)
