"""
Custom settings for the notifications app.
"""

from django.conf import settings


# Number of notifications per page
NB_NOTIFICATIONS_PER_PAGE = getattr(settings, 'NB_NOTIFICATIONS_PER_PAGE', 25)

# Number of days before a notification (read or not) is deleted.
READ_NOTIFICATION_DELETION_TIMEOUT_DAYS = getattr(settings, 'READ_NOTIFICATION_DELETION_TIMEOUT_DAYS', 30)
