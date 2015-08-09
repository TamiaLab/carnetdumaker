"""
Security token generator for the change email app.
Cloned from django.contrib.auth.tokens.
"""

from datetime import date

from django.utils import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36

from .settings import CHANGE_EMAIL_TIMEOUT_DAYS


class EmailChangeTokenGenerator(object):
    """
    Strategy object used to generate and check tokens for the change email mechanism.
    """
    key_salt = "apps.changemail.tokens.EmailChangeTokenGenerator"

    def make_token(self, user):
        """
        Returns a token that can be used once to do an email change for the given user.
        """
        return self._make_token_with_timestamp(user, self._num_days(self._today()))

    def check_token(self, user, token):
        """
        Check that an email change token is correct for a given user.
        """
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) >= CHANGE_EMAIL_TIMEOUT_DAYS:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)

        # By hashing on the internal state of the user and using state
        # that is sure to change (the email salt will change as soon as
        # the email is changed), we produce a hash that will be
        # invalid as soon as it is used.
        # We limit the hash to 20 chars to keep URL short

        hash = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)

    def _make_hash_value(self, user, timestamp):
        # Ensure results are consistent across DB backends
        return (
            six.text_type(user.pk) + user.email + six.text_type(timestamp)
        )

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        # Used for mocking in tests
        return date.today()

default_token_generator = EmailChangeTokenGenerator()
