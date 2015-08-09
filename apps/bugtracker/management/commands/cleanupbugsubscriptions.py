"""
Custom ``manage.py`` command to cleanup inactive bug tracker subscriptions.
"""

from django.core.management.base import NoArgsCommand

from apps.bugtracker.models import IssueTicketSubscription


class Command(NoArgsCommand):
    """
    A management command which deletes inactive bug tracker subscriptions from the database.
    """

    help = "Delete inactive bug tracker subscriptions from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        IssueTicketSubscription.objects.filter(active=False).delete()
