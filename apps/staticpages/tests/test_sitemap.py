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
        self.assertEqual(sitemap.location('why_this_site'), reverse('staticpages:why_this_site'))
        self.assertEqual(sitemap.location('contact_us'), reverse('staticpages:contact_us'))
        self.assertEqual(sitemap.location('cookies_usage'), reverse('staticpages:cookies_usage'))
        self.assertEqual(sitemap.location('legal_notices'), reverse('staticpages:legal_notices'))
        self.assertEqual(sitemap.location('faq'), reverse('staticpages:faq'))
        self.assertEqual(sitemap.location('our_commitments'), reverse('staticpages:our_commitments'))
        self.assertEqual(sitemap.location('human_sitemap'), reverse('staticpages:human_sitemap'))
        self.assertEqual(sitemap.location('tos'), reverse('staticpages:tos'))
