"""
Tests suite for the admin views of the user API keys app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import UserApiKey


class UserApiKeyAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_superuser(username='johndoe',
                                                                password='illpassword',
                                                                email='john.doe@example.com')
        self.api_key = UserApiKey.objects.create(user=self.author,
                                                 api_key='abcdef0123456789')

    def test_api_key_list_view_available(self):
        """
        Test the availability of the "API key list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:userapikey_userapikey_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_api_key_edit_view_available(self):
        """
        Test the availability of the "edit API key" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:userapikey_userapikey_change', args=[self.api_key.pk]))
        self.assertEqual(response.status_code, 200)
