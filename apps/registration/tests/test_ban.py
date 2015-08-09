"""
Test suite for the ban feature of the registration app.
"""

from django.test import TestCase

from ..models import (BannedUsername,
                      BannedEmail)


class BanFeatureTestCase(TestCase):
    """
    Test suite for the ban feature.
    """

    def setUp(self):
        """
        Create some test fixtures.
        """
        BannedUsername.objects.create(username='banned')
        BannedEmail.objects.create(email='banned@example.com')
        BannedEmail.objects.create(email='usernamebanned@*')
        BannedEmail.objects.create(email='*@providerbanned.com')
        BannedEmail.objects.create(email='*@providerbannedanytld.*')

    def test_username_ban(self):
        """
        Test ban by username.
        """
        self.assertFalse(BannedUsername.objects.is_username_banned('not-banned'))
        self.assertTrue(BannedUsername.objects.is_username_banned('banned'))

    def test_username_ban_case_insensitive(self):
        """
        Test ban by username (check case insensitivity).
        """
        self.assertTrue(BannedUsername.objects.is_username_banned('baNNed'))

    def test_email_ban(self):
        """
        Test ban by complete email address.
        """
        self.assertFalse(BannedEmail.objects.is_email_address_banned('not-banned@example.com'))
        self.assertTrue(BannedEmail.objects.is_email_address_banned('banned@example.com'))

    def test_email_ban_case_insensitive(self):
        """
        Test ban by complete email address (check case insensitivity).
        """
        self.assertTrue(BannedEmail.objects.is_email_address_banned('baNNed@exAMple.cOm'))

    def test_email_ban_with_any_provider(self):
        """
        Test ban by email username.
        """
        self.assertTrue(BannedEmail.objects.is_email_address_banned('usernamebanned@example.com'))
        self.assertTrue(BannedEmail.objects.is_email_address_banned('usernamebanned@localhost'))

    def test_email_ban_from_provider(self):
        """
        Test ban by email provider.
        """
        self.assertTrue(BannedEmail.objects.is_email_address_banned('toto@providerbanned.com'))
        self.assertTrue(BannedEmail.objects.is_email_address_banned('john.doe@providerbanned.com'))

    def test_email_ban_from_provider_without_tld(self):
        """
        Test ban by email provider, for any TLD.
        """
        self.assertTrue(BannedEmail.objects.is_email_address_banned('toto@providerbannedanytld.com'))
        self.assertTrue(BannedEmail.objects.is_email_address_banned('john.doe@providerbannedanytld.fr'))
