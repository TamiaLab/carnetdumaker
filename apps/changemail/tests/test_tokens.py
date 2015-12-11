"""
Tests suite for the token generators of the change email app.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from ..settings import CHANGE_EMAIL_TIMEOUT_DAYS
from ..tokens import (EmailChangeTokenGenerator,
                      default_token_generator)


class FixedEmailChangeTokenGenerator(EmailChangeTokenGenerator):
    """
    ``EmailChangeTokenGenerator`` with fixed date.
    """
    
    def __init__(self, date):
        self.date = date

    def _today(self):
        return self.date


class EmailChangeTokenGeneratorTestCase(SimpleTestCase):
    """
    Tests case for the ``EmailChangeTokenGenerator`` class.
    """

    def test_make_token_not_none(self):
        """
        Test if the ``make_token`` method return something.
        """
        user = MagicMock(pk=1, email='john.doe@example.com')
        token = default_token_generator.make_token(user)
        self.assertTrue(token)

    def test_make_token_repeatable(self):
        """
        Test if the ``make_token`` method return always the same thing in the same circumstances.
        """
        date_today = date.today()
        token_generator = FixedEmailChangeTokenGenerator(date_today)
        user = MagicMock(pk=1, email='john.doe@example.com')
        token1 = token_generator.make_token(user)
        token2 = token_generator.make_token(user)
        self.assertEqual(token1, token2)

    def test_make_token_timestamp(self):
        """
        Test if the ``make_token`` method return different token for different timestamp.
        """
        date_today = date.today()
        date_not_today = date.today() + timedelta(days=1)
        user = MagicMock(pk=1, email='john.doe@example.com')
        token1 = FixedEmailChangeTokenGenerator(date_today).make_token(user)
        token2 = FixedEmailChangeTokenGenerator(date_not_today).make_token(user)
        self.assertNotEqual(token1, token2)

    def test_make_token_user_pk(self):
        """
        Test if the ``make_token`` method return different token for different user's pk.
        """
        date_today = date.today()
        token_generator = FixedEmailChangeTokenGenerator(date_today)
        user = MagicMock(pk=1, email='john.doe@example.com')
        user2 = MagicMock(pk=2, email='john.doe@example.com')
        token1 = token_generator.make_token(user)
        token2 = token_generator.make_token(user2)
        self.assertNotEqual(token1, token2)

    def test_make_token_user_email(self):
        """
        Test if the ``make_token`` method return different token for different user's email.
        """
        date_today = date.today()
        token_generator = FixedEmailChangeTokenGenerator(date_today)
        user = MagicMock(pk=1, email='john.doe@example.com')
        user2 = MagicMock(pk=1, email='not.john.doe@example.com')
        token1 = token_generator.make_token(user)
        token2 = token_generator.make_token(user2)
        self.assertNotEqual(token1, token2)

    def test_check_token_valid(self):
        """
        Test if the ``check_token`` method return True with a valid token.
        """
        date_today = date.today()
        token_generator = FixedEmailChangeTokenGenerator(date_today)
        user = MagicMock(pk=1, email='john.doe@example.com')
        token = token_generator.make_token(user)
        self.assertTrue(token_generator.check_token(user, token))

    def test_check_token_expired(self):
        """
        Test if the ``check_token`` method return False with an expired token.
        """
        date_today = date.today()
        date_expired = date_today + timedelta(days=CHANGE_EMAIL_TIMEOUT_DAYS)
        token_generator = FixedEmailChangeTokenGenerator(date_today)
        token_generator_expired = FixedEmailChangeTokenGenerator(date_expired)
        user = MagicMock(pk=1, email='john.doe@example.com')
        token = token_generator.make_token(user)
        self.assertFalse(token_generator_expired.check_token(user, token))

    def test_check_token_invalid(self):
        """
        Test if the ``check_token`` method return False with an invalid token.
        """
        date_today = date.today()
        token_generator = FixedEmailChangeTokenGenerator(date_today)
        user = MagicMock(pk=1, email='john.doe@example.com')
        token = token_generator.make_token(user)
        token = '%sx' % token  # Tamper the signature
        self.assertFalse(token_generator.check_token(user, token))
