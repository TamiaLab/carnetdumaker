"""
Tests suite for the model fields of the timezones app.
"""

import pytz

from django.db import models
from django.test import TestCase

from ..fields import TimeZoneField


class TestModel(models.Model):
    """
    Simple test model.
    """

    timezone = TimeZoneField('Timezone',
                             default=None,
                             null=True)


class TimeZoneFieldModelTestCase(TestCase):
    """
    Tests suite for the ``TimeZoneField`` model field class.
    """

    def test_mode_instance(self):
        """
        Test if the test model can be instantiated.
        """
        model = TestModel()
        self.assertIsNotNone(model)

    def test_assign_pytz_object(self):
        """
        Test the assignation of the timezone using a pytz object.
        """
        model = TestModel()
        timezone = pytz.timezone('Europe/Paris')
        model.timezone = timezone
        self.assertEqual(model.timezone, timezone)

    def test_assign_utc_singleton(self):
        """
        Test the assignation of the timezone using the UTC singleton.
        """
        model = TestModel()
        model.timezone = pytz.UTC
        self.assertEqual(model.timezone, pytz.UTC)

    def test_assign_zone_string(self):
        """
        Test the assignation of the timezone using a zone string.
        """
        model = TestModel()
        model.timezone = 'Europe/Paris'
        self.assertEqual(model.timezone, pytz.timezone('Europe/Paris'))

    def test_assign_none(self):
        """
        Test the assignation of the timezone using None.
        """
        model = TestModel()
        model.timezone = None
        self.assertIsNone(model.timezone)

    def test_assign_empty_string(self):
        """
        Test the assignation of the timezone using the empty string.
        """
        model = TestModel()
        model.timezone = ''
        self.assertIsNone(model.timezone)
