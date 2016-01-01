"""
Custom ``manage.py`` command to cleanup inactive forum and thread "read" markers.
"""

from django.core.management.base import NoArgsCommand

from ...models import (ReadForumTracker,
                       ReadForumThreadTracker)


class Command(NoArgsCommand):
    """
    A management command which deletes inactive forum and thread "read" markers from the database.
    """

    help = "Delete inactive forum and thread \"read\" markers from the database."

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        ReadForumTracker.objects.filter(active=False).delete()
        ReadForumThreadTracker.objects.filter(active=False).delete()
