"""
Default settings for the private messages app.
"""

from django.conf import settings


# Number of days before a deleted message is (logically) deleted.
DELETED_MSG_DELETION_TIMEOUT_DAYS = getattr(settings, 'DELETED_MSG_DELETION_TIMEOUT_DAYS', 30)

# Number of days before a logically deleted message is really deleted.
DELETED_MSG_PHYSICAL_DELETION_TIMEOUT_DAYS = getattr(settings, 'DELETED_MSG_PHYSICAL_DELETION_TIMEOUT_DAYS', 365)

# Number of private message per page for list display
NB_PRIVATE_MSG_PER_PAGE = getattr(settings, 'NB_PRIVATE_MSG_PER_PAGE', 25)

# Number of seconds between two messages (anti flood, default 30s)
NB_SECONDS_BETWEEN_PRIVATE_MSG = getattr(settings, 'NB_SECONDS_BETWEEN_PRIVATE_MSG', 30)

# Number of blocked users per page for list display
NB_BLOCKED_USERS_PER_PAGE = getattr(settings, 'NB_BLOCKED_USERS_PER_PAGE', 25)
