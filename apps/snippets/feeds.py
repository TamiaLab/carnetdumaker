"""
RSS/Atom feeds for the code snippets app.
"""

from django.core.urlresolvers import reverse_lazy
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from .models import CodeSnippet
from .settings import NB_SNIPPETS_PER_FEED


class LatestCodeSnippetsFeed(Feed):
    """
    Feed of latest code snippets.
    """

    title = _('Latest code snippets')
    link = reverse_lazy('snippets:index')
    feed_url = reverse_lazy('snippets:latest_snippets_rss')
    description = _('Latest code snippets')

    def items(self):
        """
        Return a list of the N most recent code snippets.
        """
        return CodeSnippet.objects.public_snippets().select_related('author')[:NB_SNIPPETS_PER_FEED]

    def item_title(self, item):
        """
        Return the title of the code snippet.
        :param item: The current feed item.
        """
        return item.title

    def item_description(self, item):
        """
        Return the HTML of the code snippet.
        :param item: The current feed item.
        """
        return '<p>%s</p>\n<style>\n%s\n</style>\n%s' % (item.description, item.css_for_display, item.html_for_display)

    def item_author_name(self, item):
        """
        Return the author name for the code snippet.
        :param item: The current feed item.
        """
        return item.author.username if item.author.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the publication date of the code snippet.
        :param item: The current feed item.
        """
        return item.creation_date

    def item_updateddate(self, item):
        """
        Return the modification date of the code snippet.
        :param item: The current feed item.
        """
        return item.last_modification_date or item.creation_date


class LatestCodeSnippetsAtomFeed(LatestCodeSnippetsFeed):
    """
    Feed of latest code snippets (ATOM version).
    """

    feed_type = Atom1Feed
    feed_url = reverse_lazy('snippets:latest_snippets_atom')
    subtitle = LatestCodeSnippetsFeed.description
