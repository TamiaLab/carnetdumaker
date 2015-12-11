"""
Tests suite for the anti-spam app.
"""

from unittest import mock

from django import forms
from django.test import SimpleTestCase
from django.core.exceptions import NON_FIELD_ERRORS

from .settings import (MIN_TIME_FORM_GENERATION_SUBMIT,
                       MAX_TIME_FORM_GENERATION_SUBMIT)
from .forms import AntispamHoneypotFormMixin


class TestForm(AntispamHoneypotFormMixin, forms.Form):
    """
    Simple test form class.
    """
    pass


class AntiSpamMixinTestCase(SimpleTestCase):
    """
    Tests suite for the anti-spam form mixin.
    """

    def test_form_fields_exist(self):
        """
        Simple test to be sure anti-spam fields are injected into the form.
        """
        form = TestForm()
        self.assertIn('comment', form.fields)
        self.assertIn('timestamp', form.fields)

    def test_form_handle_missing_fields(self):
        """
        Test if the form handle missing fields without exception.
        """
        data = {}
        form = TestForm(data)
        self.assertFalse(form.is_valid())

        data = {
            'timestamp': ''
        }
        form = TestForm(data)
        self.assertFalse(form.is_valid())

        data = {
            'comment': ''
        }
        form = TestForm(data)
        self.assertFalse(form.is_valid())

    def test_honeypot(self):
        """
        Check if the form validation fail when the honeypot field is set.
        """

        # Generate form data with comment set
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': 'some text',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test honeypot field
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MIN_TIME_FORM_GENERATION_SUBMIT + 1

            form = TestForm(data)
            self.assertFalse(form.is_valid())
            errors = form.errors.as_data()
            self.assertEqual(len(errors), 1)
            self.assertIn('comment', errors)
            self.assertEqual(len(errors['comment']), 1)
            self.assertEqual(errors['comment'][0].code, 'bot_trapped')

    def test_disable_verification_honeypot(self):
        """
        Check if the form validation fail when the honeypot field is set and verification is disabled.
        """

        # Generate form data with comment set
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': 'some text',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test honeypot field
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MIN_TIME_FORM_GENERATION_SUBMIT + 1

            with mock.patch('apps.antispam.forms.DISABLE_ANTISPAM_VERIFICATION') as mock_setting:
                mock_setting.return_value = True

                form = TestForm(data)
                self.assertTrue(form.is_valid())

    def test_timestamp_at_min(self):
        """
        Check if the form validation fail when the timestamp min value is reached (should not).
        """

        # Generate form data
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': '',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test timestamp validation
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MIN_TIME_FORM_GENERATION_SUBMIT

            form = TestForm(data)
            self.assertTrue(form.is_valid())

    def test_timestamp_below_min(self):
        """
        Check if the form validation fail when the timestamp min value is not reached (should).
        """

        # Generate form data
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': '',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test timestamp validation
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MIN_TIME_FORM_GENERATION_SUBMIT - 1

            form = TestForm(data)
            self.assertFalse(form.is_valid())
            errors = form.errors.as_data()
            self.assertEqual(len(errors), 1)
            self.assertIn(NON_FIELD_ERRORS, errors)
            self.assertEqual(len(errors[NON_FIELD_ERRORS]), 1)
            self.assertEqual(errors[NON_FIELD_ERRORS][0].code, 'timestamp_failed')

    def test_disable_verification_timestamp_below_min(self):
        """
        Check if the form validation fail when the timestamp min value is not reached and verification is disabled.
        """

        # Generate form data
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': '',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test timestamp validation
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MIN_TIME_FORM_GENERATION_SUBMIT - 1
            with mock.patch('apps.antispam.forms.DISABLE_ANTISPAM_VERIFICATION') as mock_setting:
                mock_setting.return_value = True

                form = TestForm(data)
                self.assertTrue(form.is_valid())

    def test_timestamp_at_max(self):
        """
        Check if the form validation fail when the timestamp max value is NOT reached (should not).
        """

        # Generate form data
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': '',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test timestamp validation
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MAX_TIME_FORM_GENERATION_SUBMIT

            form = TestForm(data)
            self.assertTrue(form.is_valid())

    def test_timestamp_after_max(self):
        """
        Check if the form validation fail when the timestamp max value is reached (should).
        """

        # Generate form data
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': '',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test timestamp validation
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MAX_TIME_FORM_GENERATION_SUBMIT + 1

            form = TestForm(data)
            self.assertFalse(form.is_valid())
            errors = form.errors.as_data()
            self.assertEqual(len(errors), 1)
            self.assertIn(NON_FIELD_ERRORS, errors)
            self.assertEqual(len(errors[NON_FIELD_ERRORS]), 1)
            self.assertEqual(errors[NON_FIELD_ERRORS][0].code, 'timestamp_failed')

    def test_disable_verification_timestamp_after_max(self):
        """
        Check if the form validation fail when the timestamp max value is reached and verification is disabled.
        """

        # Generate form data
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = 0

            data = {
                'comment': '',
                'timestamp': TestForm()._generate_timestamp()
            }

        # Test timestamp validation
        with mock.patch('time.time') as mock_time:
            mock_time.return_value = MAX_TIME_FORM_GENERATION_SUBMIT + 1

            with mock.patch('apps.antispam.forms.DISABLE_ANTISPAM_VERIFICATION') as mock_setting:
                mock_setting.return_value = True

                form = TestForm(data)
                self.assertTrue(form.is_valid())
