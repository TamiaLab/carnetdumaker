"""
Dual Username/Email based authentication backend for django.contrib.auth.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


# Get user class here to avoid repeated get_user_model() calls.
UserModel = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Email based authentication backend for django.contrib.auth.
    Can be stacked after the standard username/password authentication backend to allow normal username and
    email based authentication.
    WARNING: If used, be sure to constrain uniquest on email address!
    """

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticate (or at least try to) the given user using the email address as username and the specified password.
        :param username: The user's email address.
        :param password: The user's password.
        :param kwargs: Extra arguments.
        :return: The user if authentication pass, None if authentication failed.
        """
        assert username is not None, "EmailAuthBackend is not designed for UserModel without username or email"
        try:
            user = UserModel._default_manager.get(email__iexact=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)


class CaseInsensitiveUsernameAuthBackend(ModelBackend):
    """
    Case insensitive, username based authentication backend for django.contrib.auth.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticate (or at least try to) the given user using the email address as username and the specified password.
        :param username: The user's email address.
        :param password: The user's password.
        :param kwargs: Extra arguments.
        :return: The user if authentication pass, None if authentication failed.
        """
        assert username is not None, "EmailAuthBackend is not designed for UserModel without username"
        try:
            user = UserModel._default_manager.get(username__iexact=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
