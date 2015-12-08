"""
Tests suite for the middleware of the user accounts app.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..middleware import LastActivityDateUpdateMiddleware


class LastActivityDateUpdateMiddlewareTestCase(TestCase):
    """
    Tests case for the ``LastActivityDateUpdateMiddleware`` middleware.
    """

    def test_last_activity_middleware_no_user_profile_yet(self):
        """
        Test if the LastActivityDateUpdateMiddleware is working when the user profile does not exist.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='johndoe@example.com')
        now = timezone.now()
        mw = LastActivityDateUpdateMiddleware()
        request = MagicMock(user=user)

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            result = mw.process_request(request)
            self.assertIsNone(result)

        self.assertEqual(user.user_profile.last_activity_date, now)

    def test_last_activity_middleware_user_profile_exist(self):
        """
        Test if the LastActivityDateUpdateMiddleware is working when the user profile already exist.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='johndoe@example.com')
        self.assertIsNotNone(user.user_profile)
        now = timezone.now()
        mw = LastActivityDateUpdateMiddleware()
        request = MagicMock(user=user)

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            result = mw.process_request(request)
            self.assertIsNone(result)

        user.user_profile.refresh_from_db()
        self.assertEqual(user.user_profile.last_activity_date, now)

    def test_last_activity_middleware_user_not_auth(self):
        """
        Test if the ``LastActivityDateUpdateMiddleware`` middleware is working when
        the current user is not authenticated.
        """
        mw = LastActivityDateUpdateMiddleware()
        request = MagicMock()

        request.user.is_authenticated = MagicMock(return_value=False)
        request.user.user_profile = MagicMock(return_value=None)
        result = mw.process_request(request)
        self.assertIsNone(result)
