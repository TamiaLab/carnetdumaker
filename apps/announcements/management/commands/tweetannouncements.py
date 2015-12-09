"""
Management command to cross-publish announcements on Twitter.
"""

from django.core.management.base import NoArgsCommand

from ...models import AnnouncementTwitterCrossPublication


class Command(NoArgsCommand):
    """
    A management command which cross-publish on Twitter any pending announcements
    currently published on the site but not on Twitter yet. Simply call the ``publish_pending_announcements``of
    the ``AnnouncementTwitterCrossPublication`` class to do the job.
    """

    help = "Cross-publish pending announcements on Twitter"

    def handle_noargs(self, **options):
        """
        Command handler.
        :param options: Not used.
        :return: None.
        """
        AnnouncementTwitterCrossPublication.objects.publish_pending_announcements()
