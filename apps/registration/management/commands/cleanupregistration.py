"""
Management command to cleanup expired registration database entries.
"""

from django.core.management.base import NoArgsCommand

from ...models import UserRegistrationProfile


class Command(NoArgsCommand):
    """
    A management command which deletes expired accounts (e.g.
    accounts which signed up but never activated) from the database.
    Calls ``RegistrationProfile.objects.delete_expired_users()``, which
    contains the actual logic for determining which accounts are deleted.
    """

    help = "Delete expired user registrations from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        UserRegistrationProfile.objects.delete_expired_users()
