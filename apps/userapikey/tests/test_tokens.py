"""
Tests suite for the token generators of the user API key app.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from ..tokens import default_token_generator


class ApiKeyTokenGeneratorTestCase(SimpleTestCase):
    """
    Tests case for the ``ApiKeyTokenGenerator`` class.
    """

    def test_make_token_not_none(self):
        """
        Test if the ``make_token`` method return something.
        """
        user = MagicMock(pk=1, email='john.doe@example.com')
        token = default_token_generator.make_token(user, 'abcdef0123456789')
        self.assertTrue(token)

    def test_make_token_repeatable(self):
        """
        Test if the ``make_token`` method return always the same thing in the same circumstances.
        """
        user = MagicMock(pk=1, email='john.doe@example.com')
        token1 = default_token_generator.make_token(user, 'abcdef0123456789')
        token2 = default_token_generator.make_token(user, 'abcdef0123456789')
        self.assertEqual(token1, token2)

    def test_make_token_different_key(self):
        """
        Test if the ``make_token`` method return different token for different API key.
        """
        user = MagicMock(pk=1, email='john.doe@example.com')
        token1 = default_token_generator.make_token(user, 'abcdef0123456789')
        token2 = default_token_generator.make_token(user, '0123456789abcdef')
        self.assertNotEqual(token1, token2)

    def test_make_token_different_user_pk(self):
        """
        Test if the ``make_token`` method return different token for different user's pk.
        """
        user = MagicMock(pk=1, email='john.doe@example.com')
        user2 = MagicMock(pk=2, email='john.doe@example.com')
        token1 = default_token_generator.make_token(user, 'abcdef0123456789')
        token2 = default_token_generator.make_token(user2, 'abcdef0123456789')
        self.assertNotEqual(token1, token2)

    def test_check_token_valid(self):
        """
        Test if the ``check_token`` method return True with a valid token.
        """
        user = MagicMock(pk=1, email='john.doe@example.com')
        token = default_token_generator.make_token(user, 'abcdef0123456789')
        self.assertTrue(default_token_generator.check_token(user, 'abcdef0123456789', token))

    def test_split_token(self):
        """
        Test the ``split_token`` method of the token generator.
        """
        ret = default_token_generator.split_token('1-abcdef')
        self.assertEqual((1, 'abcdef'), ret)
        ret = default_token_generator.split_token('1abcdef')
        self.assertIsNone(ret)
        ret = default_token_generator.split_token('$-abcdef')
        self.assertIsNone(ret)
        ret = default_token_generator.split_token('1-abc-def')
        self.assertEqual((1, 'abc-def'), ret)
