"""
Custom ``manage.py`` command to cleanup deleted forum's threads and posts.
"""

from django.core.management.base import NoArgsCommand

from apps.forum.models import (ForumThread,
                               ForumThreadPost)


class Command(NoArgsCommand):
    """
    A management command which deletes deleted forum's threads and posts from the database.
    """

    help = "Delete deleted forum threads and posts from the database"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        ForumThread.objects.delete_deleted_threads()
        ForumThreadPost.objects.delete_deleted_posts()
