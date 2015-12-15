"""
Custom ``manage.py`` command to cleanup old login events from history.
"""

from django.core.management.base import NoArgsCommand

from ...models import LogEvent


class Command(NoArgsCommand):
    """
    A management command which deletes old login events from the database.
    Calls ``LogEvent.objects.delete_old_events()``, which
    contains the actual logic for determining which events are deleted.
    """

    help = "Delete old login events from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        LogEvent.objects.delete_old_events()
