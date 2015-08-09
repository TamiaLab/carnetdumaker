"""
Custom settings for the database mutex app.
"""

from django.conf import settings


# Number of seconds before a lock expire (default 15min)
MUTEX_LOCK_EXPIRATION_DELAY_SEC = getattr(settings, 'MUTEX_LOCK_EXPIRATION_DELAY_SEC', 15 * 60)
