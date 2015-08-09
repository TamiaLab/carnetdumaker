"""
Tests suite for the ``utils.py`` file.
"""

import pytz

from django.test import SimpleTestCase

from ..utils import is_pytz_instance


class IsPytzInstanceTest(SimpleTestCase):
    """
    Tests suite for the ``is_pytz_instance()`` function.
    """

    def test_is_pytz_instance_UTC(self):
        """
        ``is_pytz_instance()`` must return ``True`` with ``pytz.UTC``.
        """
        self.assertTrue(is_pytz_instance(pytz.UTC))

    def test_is_pytz_instance_valid_tzinfo(self):
        """
        ``is_pytz_instance()`` must return ``True`` with any valid tzinfo instance.
        """
        self.assertTrue(is_pytz_instance(pytz.timezone('Europe/Paris')))

    def test_is_pytz_instance_invalid_tzinfo(self):
        """
        ``is_pytz_instance()`` must return ``False`` with anything other than a tzinfo instance.
        """
        self.assertFalse(is_pytz_instance('invalidtzinfo'))

    def test_is_pytz_instance_none(self):
        """
        ``is_pytz_instance()`` must return ``False`` with None.
        """
        self.assertFalse(is_pytz_instance(None))
