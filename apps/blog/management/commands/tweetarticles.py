"""
Management command to cross-publish articles on Twitter.
"""

from django.core.management.base import NoArgsCommand

from apps.dbmutex import (MutexLock,
                          AlreadyLockedError,
                          LockTimeoutError)

from ...models import ArticleTwitterCrossPublication


class Command(NoArgsCommand):
    """
    A management command which cross-publish on Twitter any pending articles
    currently published on the site but not on Twitter yet. Simply call the ``publish_pending_articles``of
    the ``ArticleTwitterCrossPublication`` class to do the job. Use the ``dbmutex`` app to avoid concurrent
    execution of the code.
    """

    help = "Cross-publish pending articles on Twitter"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """

        # Lock a critical section of code
        try:
            with MutexLock('twitter_articles'):

                # Do the job
                ArticleTwitterCrossPublication.objects.publish_pending_articles()

        except AlreadyLockedError:
            print('Could not obtain lock (another instance of the script running?)')

        except LockTimeoutError:
            print('Task completed but the lock timed out')
