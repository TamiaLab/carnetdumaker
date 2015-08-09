"""
Management command to cleanup blocked user database entries.
"""

from django.core.management.base import NoArgsCommand

from apps.privatemsg.models import BlockedUser


class Command(NoArgsCommand):
    """
    A management command which deletes any inactive blocked user from the database.
    """

    help = "Delete inactive blocked user from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        BlockedUser.objects.filter(active=False).delete()
