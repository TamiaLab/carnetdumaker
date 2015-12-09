"""
RSS/Atom feeds for the announcements app.
"""

from django.core.urlresolvers import reverse_lazy
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from .models import (Announcement,
                     AnnouncementTag)
from .settings import NB_ANNOUNCEMENTS_PER_FEED


class BaseAnnouncementsFeed(Feed):
    """
    Base class for all announcements feeds.
    """

    def items(self):
        """
        Require implementation.
        """
        raise NotImplementedError()

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

    def item_categories(self, item):
        """
        Return the list of categories of the announcement.
        :param item: The current feed item.
        """
        return [t.name for t in item.tags.all()]


class LatestAnnouncementsFeed(BaseAnnouncementsFeed):
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
        return Announcement.objects.published() \
                   .select_related('author').prefetch_related('tags')[:NB_ANNOUNCEMENTS_PER_FEED]


class LatestAnnouncementsAtomFeed(LatestAnnouncementsFeed):
    """
    Feed of latest announcements (ATOM version).
    """

    feed_type = Atom1Feed
    feed_url = reverse_lazy('announcements:latest_announcements_atom')
    subtitle = LatestAnnouncementsFeed.description


class LatestAnnouncementsForTagFeed(BaseAnnouncementsFeed):
    """
    Feed of latest announcements for a specific tag.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Return the desired ``AnnouncementTag`` object by his slug.
        :param request: The current request.
        :param args: Extra arguments.
        :param kwargs: Extra keywords arguments.
        :return: The desired ``AnnouncementTag``.
        """

        # Get desired tag slug
        slug = kwargs.pop('slug')
        assert slug is not None

        # Retrieve the tag object
        return AnnouncementTag.objects.get(slug=slug)

    def title(self, obj):
        """
        Return the title of the tag.
        :param obj: The feed object.
        """
        return _('Latest announcements with tag "%s"') % obj.name

    def link(self, obj):
        """
        Return the permalink to the tag.
        :param obj: The feed object.
        """
        return obj.get_absolute_url()

    def feed_url(self, obj):
        """
        Return the feed URL for this tag.
        :param obj: The feed object.
        """
        return obj.get_latest_announcements_rss_feed_url()

    def description(self, obj):
        """
        Return the description of the tag.
        :param obj: The feed object.
        """
        return _('Latest announcements with tag "%s"') % obj.name

    def items(self, obj):
        """
        Return all announcements for this tag.
        :param obj: The feed object.
        """
        return obj.announcements.published().select_related('author') \
                   .prefetch_related('tags')[:NB_ANNOUNCEMENTS_PER_FEED]


class LatestAnnouncementsForTagAtomFeed(LatestAnnouncementsForTagFeed):
    """
    Feed of latest announcements for a specific tag (ATOM version).
    """

    feed_type = Atom1Feed
    subtitle = LatestAnnouncementsForTagFeed.description

    def feed_url(self, obj):
        """
        Return the feed URL for this tag.
        :param obj: The feed object.
        """
        return obj.get_latest_announcements_atom_feed_url()
