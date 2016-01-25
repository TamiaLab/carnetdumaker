"""
Data models managers for the user API keys app.
"""

import uuid

from django.db import models

from .settings import USER_API_KEY_TOKEN_GENERATOR


class UserApiKeyManager(models.Manager):
    """
    Manager class for the ``UserApiKey`` data model.
    """

    def get_user_key(self, user):
        """
        Get the API key of the given user. Create a new API key if necessary.
        :param user: The related user.
        :return: The api key object related to the given user.
        """
        api_key, created = self.get_or_create(user=user, defaults={'api_key': uuid.uuid4().hex})
        return api_key

    def regenerate_user_key(self, user):
        """
        Regenerate the API key of the given user. Create a new API key if necessary.
        :param user: The related user.
        :return: The new api key object related to the given user.
        """
        api_key, created = self.update_or_create(user=user, defaults={'api_key': uuid.uuid4().hex})
        return api_key

    def get_user_by_key_token(self, api_key_token):
        """
        Get the user with the given API key token (signed API key). Check for alteration and expiration.
        :param api_key_token: The raw API key token.
        :param token_generator: The token generator to be used.
        :return: The user object or None.
        """

        # Split the raw token into parts
        parts = USER_API_KEY_TOKEN_GENERATOR.split_token(api_key_token)
        if parts is None:
            return None

        # Fetch the user API key
        uid, _ = parts
        try:
            api_key = self.get(user_id=uid)
        except self.model.DoesNotExist:
            return None

        # Check the API key token
        if not api_key.is_token_valid(api_key_token):
            return None

        # Alright gentleman
        return api_key.user
