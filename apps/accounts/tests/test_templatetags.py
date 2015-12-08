"""
Tests suite for the template tags of the user accounts app.
"""

from datetime import timedelta

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase
from django.core.urlresolvers import reverse
from django.utils.safestring import SafeString
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..templatetags.accounts import (user_profile_link,
                                     get_latest_created_user_accounts,
                                     get_latest_modified_user_accounts,
                                     get_latest_online_user_accounts)
from ..settings import ONLINE_USER_TIME_WINDOW_SECONDS


class UserProfileLinkTestCase(SimpleTestCase):
    """
    Tests case for the ``user_profile_link`` template filter tag.
    """

    def test_when_user_is_none(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user instance is ``None``.
        The result should be an empty string to avoid error in template (without hardening debug).
        """
        result = user_profile_link(None)
        self.assertEqual('', result)
        self.assertNotIsInstance(result, SafeString)

    def test_when_user_is_active(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user is active.
        The result should be a HTML ``<a>`` tag with the user's username as text and the user's profile URL as link.
        """
        user = MagicMock(is_active=True, username='johndoe')
        profile_link = reverse('accounts:user_profile', kwargs={'username': user.username})
        result = user_profile_link(user)
        excepted_result = '<a href="{url}">{username}</a>'.format(url=profile_link, username=user.username)
        self.assertEqual(excepted_result, result)
        self.assertIsInstance(result, SafeString)

    def test_conditional_escape_called(self):
        """
        Test if the ``user_profile_link`` template filter call ``conditional_escape`` on the username when autoescape
        is enabled.
        """
        user = MagicMock(is_active=True, username='johndoe')
        with patch('apps.accounts.templatetags.accounts.conditional_escape') as mock:
            mock.return_value = user.username
            user_profile_link(user)
        mock.assert_called_once_with(user.username)

    def test_conditional_escape_not_called_if_no_autoescape(self):
        """
        Test if the ``user_profile_link`` template filter call ``conditional_escape`` on the username when autoescape
        is disable.
        """
        user = MagicMock(is_active=True, username='johndoe')
        with patch('apps.accounts.templatetags.accounts.conditional_escape') as mock:
            mock.return_value = user.username
            user_profile_link(user, False)
        self.assertEqual(mock.call_count, 0)

    def test_when_user_is_not_active(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user is NOT active.
        The result should be the (not safe) string 'Anonymous'.
        """
        user = MagicMock(is_active=False, username='johndoe')
        result = user_profile_link(user)
        self.assertEqual(_('Anonymous'), result)
        self.assertNotIsInstance(result, SafeString)


class LatestCreatedAccountsTestCase(TestCase):
    """
    Tests case for the ``get_latest_created_user_accounts`` template filter tag.
    """

    def test_result(self):
        """
        Test the result of the ``get_latest_created_user_accounts`` template filter with some test data.
        """

        # Create some test users and their associated accounts
        user_1 = get_user_model().objects.create_user(username='johndoe1',
                                                      password='illpassword',
                                                      email='johndoe1@example.com')
        user_2 = get_user_model().objects.create_user(username='johndoe2',
                                                      password='illpassword',
                                                      email='johndoe2@example.com')
        user_3 = get_user_model().objects.create_user(username='johndoe3',
                                                      password='illpassword',
                                                      email='johndoe3@example.com')
        user_3.is_active = False
        user_3.save()
        user_4 = get_user_model().objects.create_user(username='johndoe4',
                                                      password='illpassword',
                                                      email='johndoe4@example.com')
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_1.user_profile)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(user_2.user_profile)
        self.assertIsNotNone(user_3)
        self.assertIsNotNone(user_3.user_profile)
        self.assertIsNotNone(user_4)
        self.assertIsNotNone(user_4.user_profile)

        # Assert template result
        latest_created_user_accounts = get_latest_created_user_accounts(5)
        self.assertQuerysetEqual(latest_created_user_accounts, ['<UserProfile: Profile of "johndoe4">',
                                                                '<UserProfile: Profile of "johndoe2">',
                                                                '<UserProfile: Profile of "johndoe1">'])

        # Assert queryset result with count limit
        latest_created_user_accounts = get_latest_created_user_accounts(2)
        self.assertQuerysetEqual(latest_created_user_accounts, ['<UserProfile: Profile of "johndoe4">',
                                                                '<UserProfile: Profile of "johndoe2">'])


class LatestModifiedAccountsTestCase(TestCase):
    """
    Tests case for the ``get_latest_modified_user_accounts`` template filter tag.
    """

    def test_result(self):
        """
        Test the result of the ``get_latest_modified_user_accounts`` template filter with some test data.
        """

        # Create some test users and their associated accounts
        user_1 = get_user_model().objects.create_user(username='johndoe1',
                                                      password='illpassword',
                                                      email='johndoe1@example.com')
        user_2 = get_user_model().objects.create_user(username='johndoe2',
                                                      password='illpassword',
                                                      email='johndoe2@example.com')
        user_3 = get_user_model().objects.create_user(username='johndoe3',
                                                      password='illpassword',
                                                      email='johndoe3@example.com')
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(user_3)
        self.assertIsNotNone(user_2.user_profile)
        self.assertIsNotNone(user_1.user_profile)
        self.assertIsNotNone(user_3.user_profile)

        # Assert template result
        latest_modified_user_accounts = get_latest_modified_user_accounts(5)
        self.assertQuerysetEqual(latest_modified_user_accounts, ['<UserProfile: Profile of "johndoe3">',
                                                                 '<UserProfile: Profile of "johndoe1">',
                                                                 '<UserProfile: Profile of "johndoe2">'])

        # Assert queryset result with count limit
        latest_modified_user_accounts = get_latest_modified_user_accounts(2)
        self.assertQuerysetEqual(latest_modified_user_accounts, ['<UserProfile: Profile of "johndoe3">',
                                                                 '<UserProfile: Profile of "johndoe1">'])


class LatestOnlineAccountsTestCase(TestCase):
    """
    Tests case for the ``get_latest_online_user_accounts`` template filter tag.
    """

    def test_result(self):
        """
        Test the result of the ``get_latest_online_user_accounts`` template filter with some test data.
        """

        # Create some test users and their associated accounts
        user_1 = get_user_model().objects.create_user(username='johndoe1',
                                                      password='illpassword',
                                                      email='johndoe1@example.com')
        user_2 = get_user_model().objects.create_user(username='johndoe2',
                                                      password='illpassword',
                                                      email='johndoe2@example.com')
        user_3 = get_user_model().objects.create_user(username='johndoe3',
                                                      password='illpassword',
                                                      email='johndoe3@example.com')
        user_4 = get_user_model().objects.create_user(username='johndoe4',
                                                      password='illpassword',
                                                      email='johndoe4@example.com')
        user_5 = get_user_model().objects.create_user(username='johndoe5',
                                                      password='illpassword',
                                                      email='johndoe5@example.com')
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_1.user_profile)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(user_2.user_profile)
        self.assertIsNotNone(user_3)
        self.assertIsNotNone(user_3.user_profile)
        self.assertIsNotNone(user_4)
        self.assertIsNotNone(user_4.user_profile)
        self.assertIsNotNone(user_5)
        self.assertIsNotNone(user_5.user_profile)

        # Set all modification dates
        now = timezone.now()
        past_now_before_threshold = now - timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS - 1)
        past_now_at_threshold = now - timedelta(seconds=ONLINE_USER_TIME_WINDOW_SECONDS)
        user_1.user_profile.last_activity_date = None
        user_1.user_profile.save()
        user_2.user_profile.last_activity_date = past_now_at_threshold
        user_2.user_profile.save()
        user_3.user_profile.last_activity_date = now
        user_3.user_profile.save()
        user_4.user_profile.online_status_public = False
        user_4.user_profile.last_activity_date = now
        user_4.user_profile.save()
        user_5.user_profile.last_activity_date = past_now_before_threshold
        user_5.user_profile.save()

        # Assert template result
        latest_online_user_accounts = get_latest_online_user_accounts(5)
        self.assertQuerysetEqual(latest_online_user_accounts, ['<UserProfile: Profile of "johndoe3">',
                                                               '<UserProfile: Profile of "johndoe5">'])

        # Assert queryset result with count limit
        latest_online_user_accounts = get_latest_online_user_accounts(1)
        self.assertQuerysetEqual(latest_online_user_accounts, ['<UserProfile: Profile of "johndoe3">'])
