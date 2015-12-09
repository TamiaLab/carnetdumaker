"""
Management command to cross-publish announcements on Twitter.
"""

from django.core.management.base import NoArgsCommand

from apps.dbmutex import MutexLock,AlreadyLockedError, LockTimeoutError

from ...models import AnnouncementTwitterCrossPublication


class Command(NoArgsCommand):
    """
    A management command which cross-publish on Twitter any pending announcements
    currently published on the site but not on Twitter yet. Simply call the ``publish_pending_announcements``of
    the ``AnnouncementTwitterCrossPublication`` class to do the job. Use the ``dbmutex`` app to avoid concurrent
    execution of the code.
    """

    help = "Cross-publish pending announcements on Twitter"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """

        # Lock a critical section of code
        try:
            with MutexLock('twitter_announcements'):

                # Do the job
                AnnouncementTwitterCrossPublication.objects.publish_pending_announcements()

        except AlreadyLockedError:
            print('Could not obtain lock (another instance of the script running?)')

        except LockTimeoutError:
            print('Task completed but the lock timed out')
