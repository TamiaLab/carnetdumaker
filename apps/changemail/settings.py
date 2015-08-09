"""
Custom default settings for the change email app.
"""

from django.conf import settings


# Number of days a "change email" link is valid (default 2 days)
CHANGE_EMAIL_TIMEOUT_DAYS = getattr(settings, 'CHANGE_EMAIL_TIMEOUT_DAYS', 2)
