"""
API key generator for the user API keys app.
Cloned from django.contrib.auth.tokens.
"""

from django.utils import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class ApiKeyTokenGenerator(object):
    """
    Strategy object used to generate and check user API keys.
    """

    key_salt = "apps.userapikey.tokens.ApiKeyTokenGenerator"

    def make_token(self, user, api_key):
        """
        Returns a token that can be used to do API call.
        :param user: The user which request the token.
        :param api_key: The current API key of the user.
        """
        return self._make_token_with_api_key(user, api_key)

    def check_token(self, user, api_key, token):
        """
        Check that an API key token is correct for a given user.
        :param user: The user which request the token.
        :param api_key: The current API key of the user.
        :param token: The token to be checked.
        """
        return constant_time_compare(self._make_token_with_api_key(user, api_key), token)

    def split_token(self, token):
        """
        Take a full API key token like "uid_b36-hash" and return a tuple (uid, hash) or None.
        :param token: The full API key token to be split.
        :return: A tuple (uid, hash) or None.
        """

        # Parse the token
        try:
            uid_b36, hash = token.split("-", maxsplit=1)
            uid_b36 = base36_to_int(uid_b36)
            return uid_b36, hash
        except ValueError:
            return None

    def _make_token_with_api_key(self, user, api_key):
        hash = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, api_key),
        ).hexdigest()
        return "%s-%s" % (int_to_base36(user.pk), hash)

    def _make_hash_value(self, user, api_key):
        # Ensure results are consistent across DB backends
        return (
            six.text_type(user.pk) + six.text_type(api_key)
        )

default_token_generator = ApiKeyTokenGenerator()
