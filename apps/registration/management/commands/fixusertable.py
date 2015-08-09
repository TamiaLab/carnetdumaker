"""
Management command to fix at the database level constrains of the ``auth_user`` table.
"""

from django.db import connection
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    """
    This management command fix at the database level constrains of the ``auth_user`` table.
    This command make the User.email field unique and indexed.
    """

    help = "Make the User.email field unique and indexed at database level."

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE auth_user ADD UNIQUE (email);")
            cursor.execute("CREATE UNIQUE INDEX auth_user_email_unique ON auth_user (email);")
