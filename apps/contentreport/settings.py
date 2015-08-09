"""
Custom settings for the content report app.
"""

from django.conf import settings


# List of user names for notification of new content report
USERNAME_LIST_FOR_CONTENT_REPORT_NOTIFICATION = getattr(settings, 'USERNAME_LIST_FOR_CONTENT_REPORT_NOTIFICATION', [])
