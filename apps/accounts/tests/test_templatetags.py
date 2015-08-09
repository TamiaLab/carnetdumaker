"""
Test suite for the template tags of the user accounts app.
"""

from unittest.mock import MagicMock

from django.test import SimpleTestCase
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.safestring import SafeString
from django.utils.translation import ugettext as _

from ..templatetags.accounts import user_profile_link


class UserProfileLinkTestCase(SimpleTestCase):
    """
    Test case for the ``user_profile_link`` template filter tag.
    """

    def test_user_is_none(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user instance is ``None``.
        The result should be an empty string to avoid error in template (without hardening debug).
        """
        result = user_profile_link(None)
        self.assertEqual(result, '')

    def test_user_is_active(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user is active.
        The result should be a HTML ``<a>`` tag with the user's username as text and the user's profile URL as link.
        """
        user = MagicMock(is_active=True, username='johndoe')
        profile_link = reverse('accounts:user_profile', kwargs={'username': user.username})
        result = user_profile_link(user)
        excepted_result = '<a href="{url}">{username}</a>'.format(url=profile_link, username=user.username)
        self.assertEqual(result, excepted_result)
        self.assertIsInstance(result, SafeString)

    def test_user_not_active(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user is NOT active.
        The result should be the (not safe) string 'Anonymous'.
        """
        user = MagicMock(is_active=False, username='johndoe')
        result = user_profile_link(user)
        self.assertEqual(result, _('Anonymous'))
        self.assertNotIsInstance(result, SafeString)

    def test_user_username_need_escape(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user is active
        and his username need escaping.
        The result should be a HTML ``<a>`` tag with the user's username as text and the user's profile URL as link.
        """
        user = MagicMock(is_active=True, username='Géo')
        profile_link = reverse('accounts:user_profile', kwargs={'username': user.username})
        result = user_profile_link(user)
        excepted_result = '<a href="{url}">{username}</a>'.format(url=profile_link, username=escape(user.username))
        self.assertEqual(result, excepted_result)
        self.assertIsInstance(result, SafeString)

    def test_user_username_autoescape_false(self):
        """
        Test the result of the ``user_profile_link`` template filter when the given user is active
        and his username need escaping but ``autoescape=False``.
        The result should be a HTML ``<a>`` tag with the user's username as text and the user's profile URL as link.
        """
        user = MagicMock(is_active=True, username='Géo')
        profile_link = reverse('accounts:user_profile', kwargs={'username': user.username})
        result = user_profile_link(user, autoescape=False)
        excepted_result = '<a href="{url}">{username}</a>'.format(url=profile_link, username=user.username)
        self.assertEqual(result, excepted_result)
        self.assertIsInstance(result, SafeString)
