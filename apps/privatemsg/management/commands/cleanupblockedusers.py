"""
Management command to cleanup deleted blocked user entries from database.
"""

from django.core.management.base import NoArgsCommand

from ...models import BlockedUser


class Command(NoArgsCommand):
    """
    A management command which deletes any inactive blocked user entries from the database.
    """

    help = "Delete inactive blocked user entries from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        BlockedUser.objects.filter(active=False).delete()
