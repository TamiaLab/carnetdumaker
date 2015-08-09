"""
Test suite for the authentication views of the registration app.
"""

from django.test import SimpleTestCase, Client
from django.core.urlresolvers import reverse


class AuthenticationViewsTestCase(SimpleTestCase):
    """
    Test suite for the authentication views.
    """

    def test_auth_index_view_redirection(self):
        """
        Test the redirection of the authentication index view to the login view.
        """
        client = Client()
        response = client.get(reverse('auth:index'))
        self.assertRedirects(response, reverse('auth:login'), status_code=301)

    def test_auth_login_view_available(self):
        """
        Test the availability of the "login" view.
        """
        client = Client()
        response = client.get(reverse('auth:login'))
        self.assertEqual(response.status_code, 200)

    def test_auth_logout_view_available(self):
        """
        Test the availability of the "logout" view.
        """
        client = Client()
        response = client.get(reverse('auth:logout'))
        self.assertEqual(response.status_code, 200)

    def test_auth_password_reset_view_available(self):
        """
        Test the availability of the "password reset" view.
        Just test the availability of the view, not the whole view (django tests already cover that).
        """
        client = Client()
        response = client.get(reverse('auth:password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_auth_password_reset_done_view_available(self):
        """
        Test the availability of the "password reset done" view.
        """
        client = Client()
        response = client.get(reverse('auth:password_reset_done'))
        self.assertEqual(response.status_code, 200)

    def test_auth_password_reset_confirm_view_available(self):
        """
        Test the availability of the "password reset confirm" view.
        Just test the availability of the view, not the whole view (django tests already cover that).
        """
        client = Client()
        response = client.get(reverse('auth:password_reset_confirm', kwargs={'uidb64': 1, 'token': 'test-token'}))
        self.assertEqual(response.status_code, 200)

    def test_auth_password_reset_complete_view_available(self):
        """
        Test the availability of the "password reset complete" view.
        """
        client = Client()
        response = client.get(reverse('auth:password_reset_complete'))
        self.assertEqual(response.status_code, 200)
