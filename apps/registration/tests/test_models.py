"""
Test suite for the models of the registration app.
"""

import datetime

from django.test import TestCase
from django.utils import timezone

from ..models import UserRegistrationProfile
from ..settings import ACCOUNT_ACTIVATION_TIMEOUT_DAYS


class UserRegistrationProfileTestCase(TestCase):
    """
    Test suite for the models.
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
        self.assertFalse(registration.activation_key_expired(now=now))

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
        self.assertTrue(registration.activation_key_expired(now=now))

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
        self.assertFalse(registration.activation_key_expired(now=now))
