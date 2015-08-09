"""
Test suite for the middleware of the user accounts app.
"""

from unittest import mock

from django.utils import timezone
from django.test import SimpleTestCase

from ..middleware import LastActivityDateUpdateMiddleware


class LastActivityDateUpdateMiddlewareTestCase(SimpleTestCase):
    """
    Test case for the ``LastActivityDateUpdateMiddleware`` middleware.
    """

    def test_last_activity_middleware(self):
        """
        Test if the LastActivityDateUpdateMiddleware is working.
        """
        now = timezone.now()
        mw = LastActivityDateUpdateMiddleware()
        request = mock.MagicMock()
        request.user.is_authenticated = mock.MagicMock(return_value=True)
        request.user.user_profile.last_activity_date = mock.MagicMock(return_value=None)
        request.user.user_profile.save = mock.MagicMock(return_value=None)
        request.user.user_profile.save_no_rendering = mock.MagicMock(return_value=None)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            result = mw.process_request(request)
            request.user.is_authenticated.assert_called_once_with()
            self.assertEqual(request.user.user_profile.last_activity_date, now)
            self.assertEqual(request.user.user_profile.save.call_count, 0)
            request.user.user_profile.save_no_rendering.assert_called_with(update_fields=('last_activity_date',))
            self.assertIsNone(result)

    def test_last_activity_middleware_user_not_auth(self):
        """
        Test if the LastActivityDateUpdateMiddleware is working when the current user is not authenticated.
        """
        mw = LastActivityDateUpdateMiddleware()
        request = mock.MagicMock()
        request.user.is_authenticated = mock.MagicMock(return_value=True)
        request.user.user_profile = mock.MagicMock(return_value=None)
        result = mw.process_request(request)
        self.assertIsNone(result)
