"""
Default settings for the registration app.
"""

from django.conf import settings


# Number of days before an activation link expire, three days by default.
ACCOUNT_ACTIVATION_TIMEOUT_DAYS = getattr(settings, 'ACCOUNT_ACTIVATION_TIMEOUT_DAYS', 3)

# Set to true to allow new user registrations (default False)
REGISTRATION_OPEN = getattr(settings, 'REGISTRATION_OPEN', False)

# Minimum size of a password in char (default 8 char)
MIN_PASSWORD_SIZE = getattr(settings, 'MIN_PASSWORD_SIZE', 8)
