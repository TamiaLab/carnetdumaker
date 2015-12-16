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

    def test_email_ban_google_dot_trick(self):
        """
        Test ban by email username with support of the Google dot trick.
        """
        ban_list = (
            'banne.d@example.com',
            'bann.ed@example.com',
            'bann.e.d@example.com',
            'ban.ned@example.com',
            'ban.ne.d@example.com',
            'ban.n.ed@example.com',
            'ban.n.e.d@example.com',
            'ba.nned@example.com',
            'ba.nne.d@example.com',
            'ba.nn.ed@example.com',
            'ba.nn.e.d@example.com',
            'ba.n.ned@example.com',
            'ba.n.ne.d@example.com',
            'ba.n.n.ed@example.com',
            'ba.n.n.e.d@example.com',
            'b.anned@example.com',
            'b.anne.d@example.com',
            'b.ann.ed@example.com',
            'b.ann.e.d@example.com',
            'b.an.ned@example.com',
            'b.an.ne.d@example.com',
            'b.an.n.ed@example.com',
            'b.an.n.e.d@example.com',
            'b.a.nned@example.com',
            'b.a.nne.d@example.com',
            'b.a.nn.ed@example.com',
            'b.a.nn.e.d@example.com',
            'b.a.n.ned@example.com',
            'b.a.n.ne.d@example.com',
            'b.a.n.n.ed@example.com',
            'b.a.n.n.e.d@example.com',
        )
        self.assertTrue(BannedEmail.objects.is_email_address_banned('banned@example.com'))
        for email in ban_list:
            self.assertTrue(BannedEmail.objects.is_email_address_banned(email), email)

    def test_email_ban_google_dot_trick_any_provider(self):
        """
        Test ban by email username with support of the Google dot trick.
        """
        BannedEmail.objects.create(email='banned@*')
        ban_list = (
            'banne.d@gmail.com',
            'bann.ed@gmail.com',
            'bann.e.d@gmail.com',
            'ban.ned@gmail.com',
            'ban.ne.d@gmail.com',
            'ban.n.ed@gmail.com',
            'ban.n.e.d@gmail.com',
            'ba.nned@gmail.com',
            'ba.nne.d@gmail.com',
            'ba.nn.ed@gmail.com',
            'ba.nn.e.d@gmail.com',
            'ba.n.ned@gmail.com',
            'ba.n.ne.d@gmail.com',
            'ba.n.n.ed@gmail.com',
            'ba.n.n.e.d@gmail.com',
            'b.anned@gmail.com',
            'b.anne.d@gmail.com',
            'b.ann.ed@gmail.com',
            'b.ann.e.d@gmail.com',
            'b.an.ned@gmail.com',
            'b.an.ne.d@gmail.com',
            'b.an.n.ed@gmail.com',
            'b.an.n.e.d@gmail.com',
            'b.a.nned@gmail.com',
            'b.a.nne.d@gmail.com',
            'b.a.nn.ed@gmail.com',
            'b.a.nn.e.d@gmail.com',
            'b.a.n.ned@gmail.com',
            'b.a.n.ne.d@gmail.com',
            'b.a.n.n.ed@gmail.com',
            'b.a.n.n.e.d@gmail.com',
        )
        self.assertTrue(BannedEmail.objects.is_email_address_banned('banned@gmail.com'))
        for email in ban_list:
            self.assertTrue(BannedEmail.objects.is_email_address_banned(email), email)
