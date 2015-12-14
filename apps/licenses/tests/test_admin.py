"""
Tests suite for the admin views of the licenses app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test.utils import override_settings

from ..models import License


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LicenseAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_superuser(username='johndoe',
                                                              password='illpassword',
                                                              email='john.doe@example.com')
        self.license = License.objects.create(name='Test 1',
                                              slug='test-1',
                                              description='Licence 1')
        License.objects.create(name='Test 2',
                               slug='test-2',
                               description='Licence 1',
                               logo='fixtures/beautifulfrog.jpg')

    def test_license_list_view_available(self):
        """
        Test the availability of the "license list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:licenses_license_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_license_edit_view_available(self):
        """
        Test the availability of the "edit license" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:licenses_license_change', args=[self.license.pk]))
        self.assertEqual(response.status_code, 200)
