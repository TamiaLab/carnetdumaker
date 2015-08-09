"""
Custom ``manage.py`` command to cleanup old notifications.
"""

from django.core.management.base import NoArgsCommand

from apps.notifications.models import Notification


class Command(NoArgsCommand):
    """
    A management command which deletes old notifications from the database.
    Calls ``Notification.objects.delete_old_notifications()``, which
    contains the actual logic for determining which notifications are deleted.
    """

    help = "Delete old notifications (read or unread) from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        Notification.objects.delete_old_notifications()
