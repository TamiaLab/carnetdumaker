"""
Tests suite for the form fields of the timezones app.
"""

from django import forms
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError

from ..forms import TimezoneFormField, coerce_to_pytz


class TestForm(forms.Form):
    """
    Simple test form.
    """

    timezone = TimezoneFormField(label='Timezone',
                                 required=False)


class TimezoneFormFieldTestCase(SimpleTestCase):
    """
    Tests suite for the ``TimezoneFormField`` form field.
    """

    def test_form_instance(self):
        """
        Test if the form can be instantiated.
        """
        form = TestForm()
        self.assertIsNotNone(form)

    def test_form_coerce(self):
        data = {'timezone': 'Europe/Paris'}
        form = TestForm(data)
        self.assertTrue(form.is_valid())
        timezone = form.cleaned_data['timezone']
        self.assertIsNotNone(timezone)
        self.assertEqual('Europe/Paris', timezone.zone)

    def test_form_empty_value(self):
        """
        Test if the form return None when timezone is not specified.
        """
        data = {'timezone': ''}
        form = TestForm(data)
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['timezone'])

    def test_form_invalid_timezone(self):
        """
        Test if the bundled ``coerce_to_pytz`` method raise ValidationError on invalid timezone names.
        """
        with self.assertRaises(ValidationError):
            coerce_to_pytz('invalid/timezone')
