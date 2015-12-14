"""
Tests suite for the sitemap of the licenses app.
"""

from django.test import TestCase
from django.conf import settings
from django.test.utils import override_settings

from ..models import License
from ..sitemap import LicensesSitemap


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LicensesSitemapTestCase(TestCase):
    """
    Tests suite for the ``LicensesSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        License.objects.create(name='Test 1',
                               slug='test-1',
                               description='Hello World!')
        License.objects.create(name='Test 3',
                               slug='test-3',
                               description='Hello World!')
        License.objects.create(name='Test 2',
                               slug='test-2',
                               description='Hello World!')

        # Test the resulting sitemap content
        sitemap = LicensesSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<License: Test 1>',
                                         '<License: Test 2>',
                                         '<License: Test 3>'])

    def test_lastmod(self):
        """
        Test the ``lastmod`` method of the sitemap with an announcement modified after being published.
        """

        # Create some test fixtures
        license = License.objects.create(name='Test 1',
                                         slug='test-1',
                                         description='Hello World!')
        self.assertIsNotNone(license.last_modification_date)

        # Test the result of the method
        sitemap = LicensesSitemap()
        self.assertEqual(sitemap.lastmod(license), license.last_modification_date)
