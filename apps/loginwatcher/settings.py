"""
Default settings for the log watcher app.
"""

from django.conf import settings


# Number of log events per page
LOG_EVENTS_PER_PAGE = getattr(settings, 'LOG_EVENTS_PER_PAGE', 10)

# Number of days before an event is deleted.
LOG_EVENT_TTL_TIMEOUT_DAYS = getattr(settings, 'LOG_EVENT_TTL_TIMEOUT_DAYS', 31 * 3)
