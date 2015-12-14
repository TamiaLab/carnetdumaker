"""
Tests suite for the views of the licenses app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings

from ..models import License


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LicenseViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.license1 = License.objects.create(name='Test 1',
                                               slug='test-1',
                                               description='Hello World!')
        self.license2 = License.objects.create(name='Test 2',
                                               slug='test-2',
                                               description='Hello World!')
        self.license3 = License.objects.create(name='Test 3',
                                               slug='test-3',
                                               description='Hello World!',
                                               logo='fixtures/beautifulfrog.jpg')

    def test_license_list_view_available(self):
        """
        Test the availability of the "license list" view.
        """
        client = Client()
        response = client.get(reverse('licenses:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'licenses/license_list.html')
        self.assertIn('licenses', response.context)
        self.assertQuerysetEqual(response.context['licenses'], ['<License: Test 1>',
                                                                '<License: Test 2>',
                                                                '<License: Test 3>'])

    def test_license_detail_view_available(self):
        """
        Test the availability of the "license detail" view.
        """
        client = Client()
        response = client.get(self.license3.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'licenses/license_detail.html')
        self.assertIn('license', response.context)
        self.assertEqual(response.context['license'], self.license3)

    def test_license_detail_view_unavailable_with_unknown_slug(self):
        """
        Test the unavailability of the "license detail" view with an unknown license's slug.
        """
        client = Client()
        response = client.get(reverse('licenses:license_detail', kwargs={'slug': 'unknown-license'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
