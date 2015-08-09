"""
Sitemap for the static pages app.
"""

from django.core.urlresolvers import reverse
from django.contrib.sitemaps import Sitemap


class StaticPagesSitemap(Sitemap):
    """
    Sitemap for all static pages.
    """

    priority = 0.3
    changefreq = 'monthly'

    def items(self):
        """ Return a list of url names for views to be include in the sitemap. """
        return ('why_this_site',
                'about_us',
                'contact_us',
                'cookies_usage',
                'legal_notices',
                'faq',
                'our_commitments',
                'human_sitemap',
                'tos')

    def location(self, item):
        """ Return the url of the given static page. """
        return reverse('staticpages:%s' % item)
