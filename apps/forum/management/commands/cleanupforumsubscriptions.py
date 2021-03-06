"""
Custom ``manage.py`` command to cleanup inactive forum and thread subscriptions.
"""

from django.core.management.base import NoArgsCommand

from ...models import (ForumSubscription,
                       ForumThreadSubscription)


class Command(NoArgsCommand):
    """
    A management command which deletes inactive forum and thread subscriptions from the database.
    """

    help = "Delete inactive forum and thread subscriptions from the database."

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        ForumSubscription.objects.filter(active=False).delete()
        ForumThreadSubscription.objects.filter(active=False).delete()
