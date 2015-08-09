"""
Tests suite for the home pages app.
"""

from django.test import SimpleTestCase, Client
from django.core.urlresolvers import reverse


class HomePagesTestCase(SimpleTestCase):
    """
    Test the availability of all home pages.
    """

    def test_main_home_page(self):
        """
        Test the availability of the main home page.
        """
        client = Client()
        response = client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')
