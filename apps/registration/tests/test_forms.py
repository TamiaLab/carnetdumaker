"""
Test suite for the forms of the registration app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import (BannedEmail,
                      BannedUsername)
from ..forms import BaseUserRegistrationForm


class BaseUserRegistrationFormTestCase(TestCase):
    """
    Test suite for the basic user registration form.
    """

    def setUp(self):
        """
        Create a test user "duplicate" with password "duplicate@example.com" for testing existing username
        and email address handling.
        Also create a banned username "banned" and a banned email address "banned@example.com" for testing
        banned username and/or email handling.
        """
        get_user_model().objects.create_user(username='duplicate',
                                             password='duplicate',
                                             email='duplicate@example.com')
        BannedUsername.objects.create(username='banned')
        BannedEmail.objects.create(email='banned@example.com')

    def test_simple_valid_form(self):
        """
        Test the form with simple valid data.
        """
        data = {
            'username': 'toto',
            'email1': 'toto@example.com',
            'email2': 'toto@example.com',
            'password1': '0123456789',
            'password2': '0123456789',
        }
        form = BaseUserRegistrationForm(data)
        self.assertTrue(form.is_valid())

    def test_username_not_allowed(self):
        """
        Test if the form detect banned username and raise validation error.
        """
        data = {
            'username': 'banned',
            'email1': 'toto@example.com',
            'email2': 'toto@example.com',
            'password1': '0123456789',
            'password2': '0123456789',
        }
        form = BaseUserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertIn('username', errors)
        self.assertEqual(len(errors['username']), 1)
        self.assertEqual('username_disallowed', errors['username'][0].code)

    def test_username_already_exist(self):
        """
        Test if the form detect already existing username and raise validation error.
        """
        data = {
            'username': 'duplicate',
            'email1': 'toto@example.com',
            'email2': 'toto@example.com',
            'password1': '0123456789',
            'password2': '0123456789',
        }
        form = BaseUserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertIn('username', errors)
        self.assertEqual(len(errors['username']), 1)
        self.assertEqual('username_already_exist', errors['username'][0].code)

    def test_email_not_allowed(self):
        """
        Test if the form detect banned email address and raise validation error.
        """
        data = {
            'username': 'toto',
            'email1': 'banned@example.com',
            'email2': 'banned@example.com',
            'password1': '0123456789',
            'password2': '0123456789',
        }
        form = BaseUserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertIn('email1', errors)
        self.assertEqual(len(errors['email1']), 1)
        self.assertEqual('email_disallowed', errors['email1'][0].code)

    def test_email_already_exist(self):
        """
        Test if the form detect already existing email address and raise validation error.
        """
        data = {
            'username': 'toto',
            'email1': 'duplicate@example.com',
            'email2': 'duplicate@example.com',
            'password1': '0123456789',
            'password2': '0123456789',
        }
        form = BaseUserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertIn('email1', errors)
        self.assertEqual(len(errors['email1']), 1)
        self.assertEqual('email_already_exist', errors['email1'][0].code)

    def test_password_mismatch(self):
        """
        Test if the form detect password mismatch and raise validation error.
        """
        data = {
            'username': 'toto',
            'email1': 'toto@example.com',
            'email2': 'toto@example.com',
            'password1': '0123456789',
            'password2': 'not 0123456789',
        }
        form = BaseUserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertIn('password2', errors)
        self.assertEqual(len(errors['password2']), 1)
        self.assertEqual('password_mismatch', errors['password2'][0].code)

    def test_email_mismatch(self):
        """
        Test if the form detect email mismatch and raise validation error.
        """
        data = {
            'username': 'toto',
            'email1': 'toto@example.com',
            'email2': 'not-toto@example.com',
            'password1': '0123456789',
            'password2': '0123456789',
        }
        form = BaseUserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertIn('email2', errors)
        self.assertEqual(len(errors['email2']), 1)
        self.assertEqual('email_mismatch', errors['email2'][0].code)
