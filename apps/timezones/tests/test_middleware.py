"""
Test suite for the ``middleware.py`` file.
"""

from unittest.mock import Mock

from django.test import TestCase, override_settings
from django.utils.timezone import get_current_timezone_name

from ..middleware import (TimezoneMiddleware,
                          TIMEZONE_SESSION_KEY)


@override_settings(TIME_ZONE='UTC')
class TimezoneMiddleWareTestCase(TestCase):

    def setUp(self):
        self.tzmware = TimezoneMiddleware()
        self.request = Mock()
        self.request.session = {}

    def test_timezone_middleware_without_session_key(self):
        """
        Test the middleware without the session key set.
        """
        self.assertEqual(None, self.tzmware.process_request(self.request))
        self.assertEqual(get_current_timezone_name(), 'UTC')

    def test_timezone_middleware_with_session_key(self):
        """
        Test the middleware with the session key set.
        """
        self.request.session = {TIMEZONE_SESSION_KEY: 'Europe/Paris'}
        self.assertEqual(None, self.tzmware.process_request(self.request))
        self.assertEqual(get_current_timezone_name(), 'Europe/Paris')
