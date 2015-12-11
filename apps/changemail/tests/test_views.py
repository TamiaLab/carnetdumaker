"""
Tests suite for the views of the change email app.
"""

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model


class ChangeEmailViewsTestCase(TestCase):
    """
    Tests case for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """

        # Create some test fixtures.
        self.user = get_user_model().objects.create_user(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')

    def test_change_email_view_available(self):
        """
        Test the availability of the "change email" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('myaccountmail:email_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'changemail/email_change_form.html')

    def test_change_email_view_redirect_not_login(self):
        """
        Test the redirection of the "change email" view when the user is not logged in.
        """
        client = Client()
        change_email_url = reverse('myaccountmail:email_change')
        response = client.get(change_email_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, change_email_url))

    def test_change_email_done_view_available(self):
        """
        Test the availability of the "change email done" view.
        """
        client = Client()
        response = client.get(reverse('myaccountmail:email_change_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'changemail/email_change_done.html')

    def test_change_email_confirm_view_available(self):
        """
        Test the availability of the "change email confirm" view.
        """
        client = Client()
        # Trigger token error to check the availability of the error page
        response = client.get(reverse('myaccountmail:email_change_confirm', kwargs={'uidb64': 'AA',
                                                                                    'addressb64': 'AA',
                                                                                    'token': 'AA-AA'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'changemail/email_change_confirm_failed.html')

    def test_change_email_complete_view_available(self):
        """
        Test the availability of the "change email complete" view.
        """
        client = Client()
        response = client.get(reverse('myaccountmail:email_change_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'changemail/email_change_complete.html')
