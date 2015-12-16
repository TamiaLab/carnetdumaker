"""
Tests suite for the models of the registration app.
"""

import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from ..models import (UserRegistrationProfile,
                      BannedUsername,
                      BannedEmail)
from ..settings import (ACCOUNT_ACTIVATION_TIMEOUT_DAYS,
                        EMAIL_RECENTLY_SENT_TIME_WINDOW_SECONDS)
from ..signals import (user_registered,
                       user_activated)


class UserRegistrationProfileTestCase(TestCase):
    """
    Tests suite for the models.
    """

    def get_john_doe(self):
        """
        Return a new inactive user named 'johndoe' with some random password and email values.
        """
        return UserRegistrationProfile.objects.create_inactive_user(username='johndoe',
                                                                    password='illpassword',
                                                                    email='john.doe@example.com')

    def test_user_creation(self):
        """
        Test the user creation.
        Check if:
        - the activation key is set to something,
        - the activation is not used by default,
        - the last key mailing date is null by default.
        Also check if the newly user is:
        - not active by default,
        - not staff,
        - not superuser (would be a big oops if it is).
        """
        registration = self.get_john_doe()
        self.assertTrue(registration.activation_key)
        self.assertFalse(registration.activation_key_used)
        self.assertEqual(registration.last_key_mailing_date, None)

        user = registration.user
        self.assertNotEqual(user, None)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_registration_profile_str(self):
        """
        Test the result of the __str__ function of ``UserRegistrationProfile`` for later tests.
        """
        registration = self.get_john_doe()
        self.assertEqual(str(registration), 'Registration profile for "johndoe"')

    def test_activation_key_expired_mail_never_sent(self):
        """
        Test if the activation key is expired (should not) when the email has never been sent yet.
        """
        registration = self.get_john_doe()
        self.assertEqual(registration.last_key_mailing_date, None)
        self.assertFalse(registration.activation_key_expired())

    def test_activation_key_expired_mail_never_sent_but_key_used(self):
        """
        Test if the activation key is expired (should) when the email has never been sent yet BUT the activation key
        has BEEN used (somehow given to the end user manually by an admin or something like this).
        """
        registration = self.get_john_doe()
        registration.activation_key_used = True
        registration.save()
        self.assertEqual(registration.last_key_mailing_date, None)
        self.assertTrue(registration.activation_key_expired())

    def test_activation_key_expired_key_used(self):
        """
        The activation expire when the key is used, whatever the last mailing date is.
        """
        registration = self.get_john_doe()
        registration.activation_key_used = True
        registration.save()
        self.assertTrue(registration.activation_key_expired())
        registration.last_key_mailing_date = timezone.now()
        registration.save()
        self.assertTrue(registration.activation_key_expired())

    def test_activation_key_expired_before_timeout(self):
        """
        Test if the activation key is expired (should not) when the key is not used yet and the timeout not reached.
        """
        now = timezone.now()
        one_second_before_timeout = now - datetime.timedelta(days=ACCOUNT_ACTIVATION_TIMEOUT_DAYS,
                                                             seconds=-1)
        registration = self.get_john_doe()
        registration.last_key_mailing_date = one_second_before_timeout
        registration.save()
        self.assertFalse(registration.activation_key_used)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            self.assertFalse(registration.activation_key_expired())

    def test_activation_key_expired_after_timeout(self):
        """
        Test if the activation key is expired (should) when the key is not used yet and the timeout is reached.
        """
        now = timezone.now()
        one_second_after_timeout = now - datetime.timedelta(days=ACCOUNT_ACTIVATION_TIMEOUT_DAYS,
                                                            seconds=1)
        registration = self.get_john_doe()
        registration.last_key_mailing_date = one_second_after_timeout
        registration.save()
        self.assertFalse(registration.activation_key_used)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            self.assertTrue(registration.activation_key_expired())

    def test_activation_key_expired_at_timeout(self):
        """
        Test if the activation key is expired (should not) when the key is not used yet and the timeout is just reached.
        """
        now = timezone.now()
        just_at_timeout = now - datetime.timedelta(days=ACCOUNT_ACTIVATION_TIMEOUT_DAYS)
        registration = self.get_john_doe()
        registration.last_key_mailing_date = just_at_timeout
        registration.save()
        self.assertFalse(registration.activation_key_used)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            self.assertFalse(registration.activation_key_expired())

    def test_activation_key_valid_with_invalid_key(self):
        """
        Test if the action key is valid when an invalid key is specified.
        """
        registration = self.get_john_doe()
        invalid_key = '0123456789test'
        self.assertFalse(registration.activation_key_valid(invalid_key))

    def test_activation_key_valid_with_valid_key(self):
        """
        Test if the action key is valid when a valid key is specified.
        """
        registration = self.get_john_doe()
        valid_key = registration.activation_key
        self.assertTrue(registration.activation_key_valid(valid_key))

    def test_activation_key_valid_with_valid_but_expired_key(self):
        """
        Test if the action key is valid when a valid but expired key is specified.
        """
        now = timezone.now()
        after_timeout = now - datetime.timedelta(days=ACCOUNT_ACTIVATION_TIMEOUT_DAYS, seconds=30)
        registration = self.get_john_doe()
        registration.last_key_mailing_date = after_timeout
        registration.save()
        valid_key = registration.activation_key
        self.assertFalse(registration.activation_key_valid(valid_key))

    def test_activate_user(self):
        """
        Test the ``activate_user`` method with an inactive user.
        """
        registration = self.get_john_doe()
        self.assertFalse(registration.user.is_active)
        registration.activate_user()
        self.assertTrue(registration.user.is_active)

    def test_activate_user_with_already_activated_user(self):
        """
        Test the ``activate_user`` method with an already active user.
        """
        registration = self.get_john_doe()
        registration.user.is_active = True
        registration.user.save()
        self.assertTrue(registration.user.is_active)
        registration.activate_user()
        self.assertTrue(registration.user.is_active)

    def test_activation_mail_was_sent_recently_true(self):
        now = timezone.now()
        just_before_timeout = now - datetime.timedelta(seconds=EMAIL_RECENTLY_SENT_TIME_WINDOW_SECONDS)
        registration = self.get_john_doe()
        registration.last_key_mailing_date = just_before_timeout
        registration.save()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            self.assertTrue(registration.activation_mail_was_sent_recently())

    def test_activation_mail_was_sent_recently_false(self):
        now = timezone.now()
        just_at_timeout = now - datetime.timedelta(seconds=EMAIL_RECENTLY_SENT_TIME_WINDOW_SECONDS + 1)
        registration = self.get_john_doe()
        registration.last_key_mailing_date = just_at_timeout
        registration.save()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            self.assertFalse(registration.activation_mail_was_sent_recently())

    def test_activation_mail_was_sent_recently_none(self):
        registration = self.get_john_doe()
        self.assertEqual(registration.last_key_mailing_date, None)
        self.assertFalse(registration.activation_mail_was_sent_recently())

    def test_signal_user_registered(self):
        """
        Test the "user registered" signal emission.
        """
        signal_received = False
        received_user = None

        def _signal_listener(sender, user, **kwargs):
            nonlocal signal_received, received_user
            signal_received = True
            received_user = user
        user_registered.connect(_signal_listener)

        registration = self.get_john_doe()

        self.assertTrue(signal_received)
        self.assertEqual(received_user, registration.user)

    def test_signal_user_activated(self):
        """
        Test the "user activated" signal emission.
        """
        registration = self.get_john_doe()
        signal_received = False
        received_user = None

        def _signal_listener(sender, user, **kwargs):
            nonlocal signal_received, received_user
            signal_received = True
            received_user = user
        user_activated.connect(_signal_listener)

        registration.activate_user()
        self.assertTrue(signal_received)
        self.assertEqual(received_user, registration.user)


class BannedUsernameTestCase(TestCase):
    """
    Tests suite for the ``BannedUsername`` class.
    """

    def test_str(self):
        """
        Test the result of the __str__ function for later tests.
        """
        banned_username = BannedUsername.objects.create(username='test')
        self.assertEqual(str(banned_username), 'test')


class BannedEmailTestCase(TestCase):
    """
    Tests suite for the ``BannedEmail`` class.
    """

    def test_str(self):
        """
        Test the result of the __str__ function for later tests.
        """
        banned_email = BannedEmail.objects.create(email='test@example.com')
        self.assertEqual(str(banned_email), 'test@example.com')
