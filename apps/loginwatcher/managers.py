"""
Data models managers for the log watcher app.
"""

import datetime

from django.db import models
from django.utils import timezone

from .settings import LOG_EVENT_TTL_TIMEOUT_DAYS


class LogEventManager(models.Manager):
    """
    Manager class for the ``LogEvent`` data model.
    """

    use_for_related_fields = True

    def delete_old_events(self, queryset=None):
        """
        Delete old login events.
        :param queryset: The queryset to be processed, if None all events are processed.
        :return: None
        """
        if not queryset:
            queryset = self.all()
        deletion_date_threshold = timezone.now() - datetime.timedelta(days=LOG_EVENT_TTL_TIMEOUT_DAYS)
        queryset.filter(event_date__lte=deletion_date_threshold).delete()
