"""
Tests suite for the sitemap of the static pages app.
"""

from django.test import SimpleTestCase
from django.core.urlresolvers import reverse

from ..sitemap import StaticPagesSitemap


class StaticPagesSitemapTestCase(SimpleTestCase):
    """
    Tests suite for the sitemap of the static pages app.
    """

    def test_items(self):
        """
        Test the ``items`` method of the sitemap.
        """
        sitemap = StaticPagesSitemap()
        self.assertEqual(sitemap.items(), ('why_this_site',
                                           'about_us',
                                           'contact_us',
                                           'cookies_usage',
                                           'legal_notices',
                                           'faq',
                                           'our_commitments',
                                           'human_sitemap',
                                           'tos'))

    def test_location(self):
        """
        Test the ``location`` method of the sitemap.
        """
        sitemap = StaticPagesSitemap()
        self.assertEqual(sitemap.location('about_us'), reverse('staticpages:about_us'))
