"""
Tests suite for the data models of the user API key app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import UserApiKey


class UserApiKeyModelTestCase(TestCase):
    """
    Tests suite for the ``UserApiKey`` data model class.
    """

    def _get_user(self):
        """
        Create some fixtures for the tests.
        :return: The newly create user.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        return user

    def test_default_values(self):
        """
        Test defaults value of a newly created API key.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.get_user_key(user)
        self.assertIsNotNone(api_key.last_generation_date)
        self.assertTrue(api_key.api_key)

    def test_str_method(self):
        """
        Test the ``__str__`` method of the model for other tests.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.get_user_key(user)
        self.assertEqual('API key of "%s"' % api_key.user.username, str(api_key))

    def test_is_token_valid_method(self):
        """
        Test the ``is_token_valid`` method of the model with a valid key.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.get_user_key(user)
        token = api_key.get_full_api_key()
        self.assertTrue(api_key.is_token_valid(token))

    def test_is_token_valid_method_invalid_key(self):
        """
        Test the ``is_token_valid`` method of the model with an invalid key.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.get_user_key(user)
        self.assertFalse(api_key.is_token_valid('HAVEYOUBEENMOOEDTODAY'))

    def test_get_user_key_with_no_key(self):
        """
        Test the ``get_user_key`` method of the manager class with a user with no API key set.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.get_user_key(user)
        self.assertIsNotNone(api_key)

    def test_get_user_key_with_key(self):
        """
        Test the ``get_user_key`` method of the manager class with a user with an API key set.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.create(user=user, api_key='abcdef012345679')
        ret = UserApiKey.objects.get_user_key(user)
        self.assertEqual(ret, api_key)

    def test_regenerate_user_key_with_no_key(self):
        """
        Test the ``regenerate_user_key`` method of the manager class with a user with no API key set.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.regenerate_user_key(user)
        self.assertIsNotNone(api_key)

    def test_regenerate_user_key_with_key(self):
        """
        Test the ``regenerate_user_key`` method of the manager class with a user with an API key set.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.create(user=user, api_key='abcdef012345679')
        ret = UserApiKey.objects.regenerate_user_key(user)
        self.assertEqual(ret, api_key)
        self.assertNotEqual(ret.api_key, api_key.api_key)
        self.assertNotEqual(ret.last_generation_date, api_key.last_generation_date)

    def test_get_user_by_key_token_with_invalid_token_format(self):
        """
        Test the ``get_user_by_key_token`` method of the manager class with .
        """
        ret = UserApiKey.objects.get_user_by_key_token('LULZ')
        self.assertIsNone(ret)

    def test_get_user_by_key_token_with_no_key(self):
        """
        Test the ``get_user_by_key_token`` method of the manager class with .
        """
        ret = UserApiKey.objects.get_user_by_key_token('1337-LULZ')
        self.assertIsNone(ret)

    def test_get_user_by_key_token_with_invalid_token(self):
        """
        Test the ``get_user_by_key_token`` method of the manager class with .
        """
        user = self._get_user()
        api_key = UserApiKey.objects.get_user_key(user)
        token = api_key.get_full_api_key()
        ret = UserApiKey.objects.get_user_by_key_token(token + 'x')
        self.assertIsNone(ret)

    def test_get_user_by_key_token(self):
        """
        Test the ``get_user_by_key_token`` method of the manager class with a valid token.
        """
        user = self._get_user()
        api_key = UserApiKey.objects.get_user_key(user)
        token = api_key.get_full_api_key()
        ret = UserApiKey.objects.get_user_by_key_token(token)
        self.assertEqual(user, ret)
