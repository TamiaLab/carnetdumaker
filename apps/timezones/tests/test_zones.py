"""
Tests suite for the ``zones.py`` file.
"""

import pytz
from datetime import datetime

from django.test import SimpleTestCase

from ..zones import (prettify_tz,
                     ALL_TIMEZONE_CHOICES,
                     COMMON_TIMEZONE_CHOICES,
                     PRETTY_TIMEZONE_CHOICES)


class ZonesTest(SimpleTestCase):
    """
    Tests suite for the ``zones.py`` file.
    """

    def _assert_tz_in_tuple(self, tz_lists, tz_tuples, transform_fnct=lambda x: x):
        """
        Test if all timezone in ``tz_lists`` can be found in ``tz_tuples``.
        :param tz_lists: tuple
        :param tz_tuples: tuple
        :return: None
        """
        # Assert tuple size to avoid any duplicate
        self.assertEqual(len(tz_lists), len(tz_tuples))
        tz_dict = dict(tz_tuples)
        for zone in tz_lists:
            # Check if all timezones exist
            self.assertTrue(zone in tz_dict)
            self.assertEqual(transform_fnct(zone), tz_dict[zone])

    def test_all_timezones_in_ALL_TIMEZONE_CHOICES(self):
        """
        Test if all timezone in ``pytz.all_timezones`` can be found in ``ALL_TIMEZONE_CHOICES``.
        :return: None
        """
        self._assert_tz_in_tuple(pytz.all_timezones, ALL_TIMEZONE_CHOICES)

    def test_common_timezones_in_COMMON_TIMEZONE_CHOICES(self):
        """
        Test if all timezone in ``pytz.common_timezones`` can be found in ``COMMON_TIMEZONE_CHOICES``.
        :return: None
        """
        self._assert_tz_in_tuple(pytz.common_timezones, COMMON_TIMEZONE_CHOICES)

    def test_prettify_tz_function(self):
        """
        Test the ``prettify_tz()`` function.
        :return: None
        """
        utc_offset = datetime.now(pytz.timezone('Europe/Paris')).strftime('%z')
        self.assertEqual('(UTC%s) Europe/Paris' % utc_offset, prettify_tz('Europe/Paris'))

    def test_PRETTY_TIMEZONE_CHOICES_is_sorted(self):
        """
        Test if ``PRETTY_TIMEZONE_CHOICES`` is sorted by alphanumeric order.
        :return: None
        """
        sorted_tz = sorted(PRETTY_TIMEZONE_CHOICES, key=lambda x: x[1])
        self.assertEqual(sorted_tz, PRETTY_TIMEZONE_CHOICES)

    def test_pretty_timezones_in_PRETTY_TIMEZONE_CHOICES(self):
        """
        Test if all timezone in ``pytz.common_timezones`` can be found in ``PRETTY_TIMEZONE_CHOICES``.
        :return: None
        """
        self._assert_tz_in_tuple(pytz.common_timezones, PRETTY_TIMEZONE_CHOICES, transform_fnct=prettify_tz)
