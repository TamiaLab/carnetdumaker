"""
Management command to redo all code snippets highlighting.
"""

from django.core.management.base import NoArgsCommand

from apps.snippets.models import CodeSnippet


class Command(NoArgsCommand):
    """
    A management command which redo all code snippets highlighting. Call
    ``CodeSnippet.objects.redo_highlighting()`` for doing the job.
    """

    help = "Redo all code snippets highlighting"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        CodeSnippet.objects.redo_highlighting()
