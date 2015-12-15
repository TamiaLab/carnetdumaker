"""
Management command to cleanup deleted private message from database.
"""

from django.core.management.base import NoArgsCommand

from ...models import PrivateMessage


class Command(NoArgsCommand):
    """
    A management command which deletes deleted private messages from the database.
    Calls ``PrivateMessage.objects.delete_deleted_msg()``, which
    contains the actual logic for determining which messages are deleted.
    """

    help = "Delete deleted private messages from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        PrivateMessage.objects.delete_deleted_msg()
