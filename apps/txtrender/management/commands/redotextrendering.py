"""
Management command to redo text rendering of all rich text fields in the database.
"""

from django.core.management.base import NoArgsCommand

from ...signals import render_engine_changed


class Command(NoArgsCommand):
    """
    A management command which force all rich text fields in the database to be
    regenerated from the source text.
    Send the signal ``render_engine_changed`` and let all listening applications
    to handle the signal and redo rendering.
    """

    help = "Redo text rendering of all rich text fields in the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        render_engine_changed.send(sender=self.__class__)
