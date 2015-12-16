"""
Tests suite for the admin views of the registration app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import (UserRegistrationProfile,
                      BannedUsername,
                      BannedEmail)


class UserRegistrationProfileAdminTestCase(TestCase):
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
        self.profile = UserRegistrationProfile.objects.create(user=self.user,
                                                              activation_key='0123456789')

    def test_user_registration_profile_list_view_available(self):
        """
        Test the availability of the "user registration profile list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:registration_userregistrationprofile_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_private_message_edit_view_available(self):
        """
        Test the availability of the "edit user registration profile" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:registration_userregistrationprofile_change', args=[self.profile.pk]))
        self.assertEqual(response.status_code, 200)


class BannedUsernameAdminTestCase(TestCase):
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
        self.ban = BannedUsername.objects.create(username='test')

    def test_banned_username_list_view_available(self):
        """
        Test the availability of the "banned username list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:registration_bannedusername_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_banned_username_edit_view_available(self):
        """
        Test the availability of the "edit banned username" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:registration_bannedusername_change', args=[self.ban.pk]))
        self.assertEqual(response.status_code, 200)


class BannedEmailAdminTestCase(TestCase):
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
        self.ban = BannedEmail.objects.create(email='test@example.com')

    def test_banned_email_list_view_available(self):
        """
        Test the availability of the "banned email list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:registration_bannedemail_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_banned_email_edit_view_available(self):
        """
        Test the availability of the "edit banned email" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:registration_bannedemail_change', args=[self.ban.pk]))
        self.assertEqual(response.status_code, 200)
