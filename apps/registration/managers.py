"""
Objects managers for the registration app.
"""

import re
import uuid

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model

from .signals import user_registered


class UserRegistrationManager(models.Manager):
    """
    ``UserRegistrationProfile`` objects manager.
    """

    @staticmethod
    def _generate_new_activation_key():
        """
        Generate a new (random) activation key of 32 alphanumeric characters.
        """
        return uuid.uuid4().hex

    def create_inactive_user(self, username, email, password):
        """
        Create a new inactive user using the given username, email and password.
        Also create an ``UserRegistrationProfile`` for the newly created user.
        Once the ``User`` and ``UserRegistrationProfile`` are created, send the
        ``user_registered`` signal for other apps to do their jobs.
        Return the created ``UserRegistrationProfile`` for any external purpose.
        :param username: The user's username.
        :param email: The user's email address.
        :param password: The user's password (plain text).
        """
        new_user = get_user_model().objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()
        registration_profile = self._create_profile(new_user)
        user_registered.send(sender=UserRegistrationManager, user=new_user)
        return registration_profile

    def _create_profile(self, user):
        """
        Create a new ``UserRegistrationProfile`` for the given user.
        """
        activation_key = self._generate_new_activation_key()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self, queryset=None):
        """
        Remove expired instances of ``UserRegistrationProfile`` and their
        associated ``User``s.
        Accounts to be deleted are identified by searching for
        instances of ``UserRegistrationProfile`` with NOT USED expired activation
        keys, and then checking to see if their associated ``User``
        instances have the field ``is_active`` set to ``False``; any
        ``User`` who is both inactive and has a not used expired activation
        key will be deleted. If the key has been used, the ``User`` will not
        be deleted. This allow administrators to disable accounts temporally.
        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupregistration``.
        Regularly clearing out accounts which have never been
        activated serves two useful purposes:
        1. It alleviates the occasional need to reset a
           ``UserRegistrationProfile`` and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.
        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those usernames to anyone else); since
           those accounts will be deleted, the usernames will become
           available for use again.
        :param queryset: If the ``queryset`` parameter is not specified the cleanup process will run on
        all the ``UserRegistrationProfile`` entries currently in database.
        """
        if not queryset:
            queryset = self.all()
        # Delete all used activation key (optimal way)
        queryset.filter(activation_key_used=True).delete()
        # Delete all expired (but not used) activation key
        # The filter(activation_key_used=False) avoid running race
        for profile in queryset.filter(activation_key_used=False):
            if profile.activation_key_expired():
                try:
                    user = profile.user
                    if not user.is_active:
                        user.delete()
                except get_user_model().DoesNotExist:
                    pass
                profile.delete()


class BannedUsernameManager(models.Manager):
    """
    ``BannedUsername`` objects manager.
    """

    def is_username_banned(self, username):
        """
        Test if the given username is banned or not.
        :param username: The username to be checked.
        """
        return self.filter(username__iexact=username).exists()


class BannedEmailManager(models.Manager):
    """
    ``BannedEmail`` objects manager.
    """

    def is_email_address_banned(self, email_address):
        """
        Test if the given email address is banned or not.
        :param email_address: The email address to be check.
        """
        email_username, email_provider = email_address.split('@')
        email_provider_no_tld = email_provider.rsplit('.', 1)[0]
        banned = self.filter(Q(email__iexact=email_address) |
                             Q(email__iexact='%s@*' % email_username) |
                             Q(email__iexact='*@%s' % email_provider) |
                             Q(email__iexact='*@%s.*' % email_provider_no_tld)).exists()
        if not banned:
            # Use regex to get ride of Gmail dot trick
            email_username_no_dot = email_username.replace('.', '')
            username_re = r'\.?'.join(re.escape(email_username_no_dot))
            provider_re = re.escape(email_provider)
            return self.filter(email__iregex=r'^%s@(\*|%s)$' % (username_re, provider_re)).exists()
        return True
