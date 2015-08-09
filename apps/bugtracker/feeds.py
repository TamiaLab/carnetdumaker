"""
RSS/Atom feeds for the bug tracker app.
"""

from django.core.urlresolvers import reverse_lazy
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from .models import (IssueTicket,
                     IssueComment)
from .settings import (NB_ISSUES_IN_RECENT_ISSUE_FEED,
                       NB_COMMENTS_IN_RECENT_COMMENT_FEED)


class LatestTicketsFeed(Feed):
    """
    Feed of latest tickets.
    """

    title = _('Latest issue tickets')
    link = reverse_lazy('bugtracker:issues_list')
    description = _('Latest issue tickets')

    def items(self):
        """
        Return a list of the most recent tickets.
        """
        return IssueTicket.objects.select_related('submitter', 'component') \
                   .order_by('-submission_date')[:NB_ISSUES_IN_RECENT_ISSUE_FEED]

    def item_title(self, item):
        """
        Return the title of the ticket.
        """
        return item.title

    def item_description(self, item):
        """
        Return the description of the ticket.
        """
        return item.description_html

    def item_author_name(self, item):
        """
        Return the author name for the ticket.
        """
        submitter = item.submitter
        return submitter.username if submitter.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the submitted date of the ticket.
        """
        return item.submission_date

    def item_updateddate(self, item):
        """
        Return the last modification date of the ticket.
        """
        return item.last_modification_date

    def item_categories(self, item):
        """
        Return the categories of the ticket.
        """
        return item.component.name, item.status, item.priority, item.difficulty


class LatestTicketsAtomFeed(LatestTicketsFeed):
    """
    Feed of latest tickets (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestTicketsFeed.description


class LatestTicketCommentsFeed(Feed):
    """
    Feed of latest ticket's comments.
    """

    title = _('Latest comments')
    link = reverse_lazy('bugtracker:issues_list')
    description = _('Latest comments, all tickets together')

    def items(self):
        """
        Return a list of the most recent ticket's comments.
        """
        return IssueComment.objects.select_related('issue', 'author') \
                   .order_by('-pub_date')[:NB_COMMENTS_IN_RECENT_COMMENT_FEED]

    def item_title(self, item):
        """
        Return the title of the parent issue.
        """
        return item.issue.title

    def item_description(self, item):
        """
        Return the description of the comment.
        """
        return item.body_html

    def item_author_name(self, item):
        """
        Return the author name for the comment.
        """
        author = item.author
        return author.username if author.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the submitted date of the comment.
        """
        return item.pub_date


class LatestTicketCommentsAtomFeed(LatestTicketCommentsFeed):
    """
    Feed of latest ticket's comments (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestTicketCommentsFeed.description


class LatestTicketCommentsForIssueFeed(Feed):
    """
    Feed of latest ticket's comments for a given ticket.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Get the desired ticket.
        """

        # Get desired issue PK
        pk = kwargs.pop('pk')
        assert pk is not None

        # Get the issue
        return IssueTicket.objects.select_related('submitter', 'component').get(pk=pk)

    def title(self, obj):
        """
        Return the title of the ticket.
        """
        return _('Latest comments for ticket #%d') % obj.pk

    def link(self, obj):
        """
        Return the permalink to the ticket.
        """
        return obj.get_absolute_url()

    def description(self, obj):
        """
        Return the description of the ticket.
        """
        return _('Latest comments for ticket #%d') % obj.pk

    def author_name(self, obj):
        """
        Return the author name of the ticket.
        """
        submitter = obj.submitter
        return submitter.username if submitter.is_active else _('Anonymous')

    def categories(self, obj):
        """
        Return the categories of the ticket.
        """
        return obj.component.name, obj.status, obj.priority, obj.difficulty

    def items(self, obj):
        """
        Return all comments of the ticket.
        """
        return obj.comments.select_related('issue', 'author') \
                   .order_by('-pub_date')[:NB_COMMENTS_IN_RECENT_COMMENT_FEED]

    def item_title(self, item):
        """
        Return the title of the parent issue.
        """
        return item.issue.title

    def item_description(self, item):
        """
        Return the description of the comment.
        """
        return item.body_html

    def item_author_name(self, item):
        """
        Return the author name for the comment.
        """
        author = item.author
        return author.username if author.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the submitted date of the comment.
        """
        return item.pub_date


class LatestTicketCommentsForIssueAtomFeed(LatestTicketCommentsForIssueFeed):
    """
    Feed of latest ticket's comments for the given issue (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestTicketCommentsForIssueFeed.description
