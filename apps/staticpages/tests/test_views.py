"""
Tests cases for the static pages app.
"""

from django.test import SimpleTestCase, Client
from django.core.urlresolvers import reverse


class StaticPagesTestCase(SimpleTestCase):
    """
    Test the availability of all static pages.
    """

    def test_static_page_index(self):
        """
        Test the availability of the "index" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/index.html')

    def test_static_page_why_this_site(self):
        """
        Test the availability of the "why this site?" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:why_this_site'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/why_this_site.html')

    def test_static_page_about_us(self):
        """
        Test the availability of the "about us" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/about_us.html')

    def test_static_page_contact_us(self):
        """
        Test the availability of the "contact us" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/contact_us.html')

    def test_static_page_cookies_usage(self):
        """
        Test the availability of the "cookies usage" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:cookies_usage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/cookies_usage.html')

    def test_static_page_legal_notices(self):
        """
        Test the availability of the "legal notices" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:legal_notices'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/legal_notices.html')

    def test_static_page_faq(self):
        """
        Test the availability of the "FAQ" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/faq.html')

    def test_static_page_our_commitments(self):
        """
        Test the availability of the "our commitments" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:our_commitments'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/our_commitments.html')

    def test_static_page_human_sitemap(self):
        """
        Test the availability of the "sitemap" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:human_sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/human_sitemap.html')

    def test_static_page_tos(self):
        """
        Test the availability of the "Terms of service" static page.
        """
        client = Client()
        response = client.get(reverse('staticpages:tos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/tos.html')
