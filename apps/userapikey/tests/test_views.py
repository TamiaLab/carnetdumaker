"""
Tests suite for the views of the user API key app.
"""

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import UserApiKey


class UserApiKeyViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        self.api_key = UserApiKey.objects.create(user=author,
                                                 api_key='abcdef0123456789')

    def test_api_key_view_available(self):
        """
        Test the availability of the "my API key" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('userapikey:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userapikey/show_mykey.html')
        self.assertIn('api_key', response.context)
        self.assertEqual(response.context['api_key'], self.api_key)

    def test_api_key_view_redirect_not_login(self):
        """
        Test the redirection of the "my API key" view when not logged-in.
        """
        client = Client()
        my_api_key_url = reverse('userapikey:index')
        response = client.get(my_api_key_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, my_api_key_url))

    def test_regenerate_api_key_view_available(self):
        """
        Test the availability of the "regenerate my API key" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('userapikey:regen_mykey'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userapikey/regen_mykey_form.html')

    def test_regenerate_api_key_view_redirect_not_login(self):
        """
        Test the redirection of the "regenerate my API key" view when not logged-in.
        """
        client = Client()
        regen_my_api_key_url = reverse('userapikey:regen_mykey')
        response = client.get(regen_my_api_key_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, regen_my_api_key_url))

    def test_api_key_view_available_new_user(self):
        """
        Test the availability of the "my API key" view with a new user.
        """
        user = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.johnsmith@example.com')
        client = Client()
        client.login(username='johnsmith', password='illpassword')
        response = client.get(reverse('userapikey:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userapikey/show_mykey.html')
        self.assertIn('api_key', response.context)
        self.assertEqual(response.context['api_key'].user, user)
