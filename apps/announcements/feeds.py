"""
RSS/Atom feeds for the announcements app.
"""

from django.core.urlresolvers import reverse_lazy
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from .models import Announcement
from .settings import NB_ANNOUNCEMENTS_PER_FEED


class LatestAnnouncementsFeed(Feed):
    """
    Feed of latest announcements.
    """

    title = _('Latest announcements')
    link = reverse_lazy('announcements:index')
    feed_url = reverse_lazy('announcements:latest_announcements_rss')
    description = _('Latest announcements')

    def items(self):
        """
        Return a list of the N most recent announcements.
        """
        return Announcement.objects.published().select_related('author')[:NB_ANNOUNCEMENTS_PER_FEED]

    def item_title(self, item):
        """
        Return the title of the announcement.
        :param item: The current feed item.
        """
        return item.title

    def item_description(self, item):
        """
        Return the description of the announcement.
        :param item: The current feed item.
        """
        return item.content_html

    def item_author_name(self, item):
        """
        Return the author name for the announcement.
        :param item: The current feed item.
        """
        return item.author.username if item.author.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the published date of the announcement.
        :param item: The current feed item.
        """
        return item.pub_date

    def item_updateddate(self, item):
        """
        Return the last content modification date of the announcement.
        :param item: The current feed item.
        """
        return item.last_content_modification_date or item.pub_date


class LatestAnnouncementsAtomFeed(LatestAnnouncementsFeed):
    """
    Feed of latest announcements (ATOM version).
    """

    feed_type = Atom1Feed
    feed_url = reverse_lazy('announcements:latest_announcements_atom')
    subtitle = LatestAnnouncementsFeed.description
