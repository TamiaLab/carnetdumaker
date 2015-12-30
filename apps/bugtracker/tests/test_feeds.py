"""
Tests suite for the feeds of the bug tracker app.
"""

from datetime import timedelta, datetime
from unittest.mock import MagicMock

from django.test import SimpleTestCase, TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from ..models import (AppComponent,
                      IssueTicket,
                      IssueComment)
from ..settings import (NB_ISSUES_IN_RECENT_ISSUE_FEED,
                        NB_COMMENTS_IN_RECENT_COMMENT_FEED)
from ..feeds import (LatestTicketsFeed,
                     LatestTicketsAtomFeed,
                     LatestTicketCommentsFeed,
                     LatestTicketCommentsAtomFeed,
                     LatestTicketCommentsForIssueFeed,
                     LatestTicketCommentsForIssueAtomFeed)


class LatestTicketsFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestTicketsFeed`` feed class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestTicketsFeed()
        self.assertEqual(feed.title, _('Latest issue tickets'))
        self.assertEqual(feed.link, reverse('bugtracker:issues_list'))
        self.assertEqual(feed.feed_url, reverse('bugtracker:latest_issues_rss'))
        self.assertEqual(feed.description, _('Latest issue tickets'))

    def test_feed_items(self):
        """
        Test the items returned by the ``items`` method of the feed.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket',
                                            description='Test',
                                            submitter=user,
                                            assigned_to=user)
        self.assertIsNotNone(ticket)

        feed = LatestTicketsFeed()
        queryset = feed.items()
        self.assertQuerysetEqual(queryset, ['<IssueTicket: Test ticket>'])

    def test_items_limit(self):
        """
        Test if only the N most recent tickets are included in the feed.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        tickets = []
        for i in range(NB_ISSUES_IN_RECENT_ISSUE_FEED + 5):
            obj = IssueTicket.objects.create(title='Test ticket',
                                             description='Test',
                                             submitter=user,
                                             assigned_to=user)
            tickets.append(repr(obj))

        # Test the object in the feed
        feed = LatestTicketsFeed()
        items = feed.items()
        self.assertQuerysetEqual(items, tickets[:NB_ISSUES_IN_RECENT_ISSUE_FEED])

    def test_item_title(self):
        """
        Test the base ``item_title`` method.
        """
        item = MagicMock(title='Test')
        feed = LatestTicketsFeed()
        self.assertEqual(item.title, feed.item_title(item))

    def test_item_description(self):
        """
        Test the base ``item_description`` method.
        """
        item = MagicMock(description_html='Test')
        feed = LatestTicketsFeed()
        self.assertEqual(item.description_html, feed.item_description(item))

    def test_item_author_name(self):
        """
        Test the base ``item_author_name`` method.
        """
        item = MagicMock()
        item.submitter = MagicMock(username='Johndoe', is_active=True)
        feed = LatestTicketsFeed()
        self.assertEqual(item.submitter.username, feed.item_author_name(item))

    def test_item_author_name_anonymous(self):
        """
        Test the base ``item_author_name`` method with an inactive user.
        """
        item = MagicMock()
        item.submitter = MagicMock(username='Johndoe', is_active=False)
        feed = LatestTicketsFeed()
        self.assertEqual(_('Anonymous'), feed.item_author_name(item))

    def test_item_pubdate(self):
        """
        Test the base ``item_pubdate`` method.
        """
        item = MagicMock(submission_date=timezone.now())
        feed = LatestTicketsFeed()
        self.assertEqual(item.submission_date, feed.item_pubdate(item))

    def test_item_updateddate(self):
        """
        Test the base ``item_updateddate`` method.
        """
        item = MagicMock(last_modification_date=timezone.now())
        feed = LatestTicketsFeed()
        self.assertEqual(item.last_modification_date, feed.item_updateddate(item))

    def test_item_categories(self):
        """
        Test the base ``item_categories`` method.
        """
        item = MagicMock(status='Test status', priority='Test priority', difficulty='Test difficulty')
        item.component = MagicMock(name='Test app')
        feed = LatestTicketsFeed()
        self.assertEqual(feed.item_categories(item),
                         (item.component.name, item.status, item.priority, item.difficulty))

    def test_item_categories_no_component(self):
        """
        Test the base ``item_categories`` method.
        """
        item = MagicMock(component=None, status='Test status', priority='Test priority', difficulty='Test difficulty')
        feed = LatestTicketsFeed()
        self.assertEqual(feed.item_categories(item), (item.status, item.priority, item.difficulty))


class LatestTicketsAtomFeedTestCase(SimpleTestCase):
    """
    Tests suite for the ``LatestTicketsAtomFeed`` feed class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestTicketsAtomFeed()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.title, LatestTicketsFeed.title)
        self.assertEqual(feed.link, LatestTicketsFeed.link)
        self.assertEqual(feed.feed_url, reverse('bugtracker:latest_issues_atom'))
        self.assertEqual(feed.subtitle, LatestTicketsFeed.description)


class LatestTicketCommentsFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestTicketCommentsFeed`` feed class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestTicketCommentsFeed()
        self.assertEqual(feed.title, _('Latest comments'))
        self.assertEqual(feed.link, reverse('bugtracker:issues_list'))
        self.assertEqual(feed.feed_url, reverse('bugtracker:latest_issue_comments_rss'))
        self.assertEqual(feed.description, _('Latest comments, all tickets together'))

    def test_feed_items(self):
        """
        Test the items returned by the ``items`` method of the feed.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket',
                                            description='Test',
                                            submitter=user,
                                            assigned_to=user)
        comment = IssueComment.objects.create(issue=ticket,
                                              author=user,
                                              body='Test comment')
        self.assertIsNotNone(comment)

        feed = LatestTicketCommentsFeed()
        queryset = feed.items()
        self.assertQuerysetEqual(queryset, ['<IssueComment: Comment for issue "Test ticket": "Test comment\n\n...">'])

    def test_items_limit(self):
        """
        Test if only the N most recent tickets are included in the feed.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket',
                                            description='Test',
                                            submitter=user,
                                            assigned_to=user)
        comments = []
        for i in range(NB_COMMENTS_IN_RECENT_COMMENT_FEED + 5):
            obj = IssueComment.objects.create(issue=ticket,
                                              author=user,
                                              body='Test comment')
            comments.append(repr(obj))

        # Test the object in the feed
        feed = LatestTicketCommentsFeed()
        items = feed.items()
        self.assertQuerysetEqual(items, comments[:NB_COMMENTS_IN_RECENT_COMMENT_FEED])

    def test_item_title(self):
        """
        Test the base ``item_title`` method.
        """
        item = MagicMock()
        item.issue = MagicMock(title='Test')
        feed = LatestTicketCommentsFeed()
        self.assertEqual(item.issue.title, feed.item_title(item))

    def test_item_description(self):
        """
        Test the base ``item_description`` method.
        """
        item = MagicMock(body_html='Test')
        feed = LatestTicketCommentsFeed()
        self.assertEqual(item.body_html, feed.item_description(item))

    def test_item_author_name(self):
        """
        Test the base ``item_author_name`` method.
        """
        item = MagicMock()
        item.author = MagicMock(username='Johndoe', is_active=True)
        feed = LatestTicketCommentsFeed()
        self.assertEqual(item.author.username, feed.item_author_name(item))

    def test_item_author_name_anonymous(self):
        """
        Test the base ``item_author_name`` method with an inactive user.
        """
        item = MagicMock()
        item.author = MagicMock(username='Johndoe', is_active=False)
        feed = LatestTicketCommentsFeed()
        self.assertEqual(_('Anonymous'), feed.item_author_name(item))

    def test_item_pubdate(self):
        """
        Test the base ``item_pubdate`` method.
        """
        item = MagicMock(pub_date=timezone.now())
        feed = LatestTicketCommentsFeed()
        self.assertEqual(item.pub_date, feed.item_pubdate(item))

    def test_item_updateddate(self):
        """
        Test the base ``item_updateddate`` method.
        """
        item = MagicMock(last_modification_date=timezone.now())
        feed = LatestTicketCommentsFeed()
        self.assertEqual(item.last_modification_date, feed.item_updateddate(item))


class LatestTicketCommentsAtomFeedTestCase(SimpleTestCase):
    """
    Tests suite for the ``LatestTicketCommentsAtomFeed`` feed class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestTicketCommentsAtomFeed()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.title, LatestTicketCommentsFeed.title)
        self.assertEqual(feed.link, LatestTicketCommentsFeed.link)
        self.assertEqual(feed.feed_url, reverse('bugtracker:latest_issue_comments_atom'))
        self.assertEqual(feed.subtitle, LatestTicketCommentsFeed.description)


class LatestTicketCommentsForIssueFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestTicketCommentsForIssueFeed`` feed class.
    """

    def setUp(self):
        """
        Create some test fixtures for all tests.
        """
        self.user = get_user_model().objects.create_user(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')
        self.ticket = IssueTicket.objects.create(title='Test ticket',
                                                 description='Test',
                                                 submitter=self.user,
                                                 assigned_to=self.user)

    def test_feed_get_object(self):
        """
        Test the ``get_object`` method of the feed.
        """
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.get_object(None, pk=self.ticket.pk), self.ticket)

    def test_feed_title(self):
        """
        Test the ``title`` method of the feed.
        """
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.title(self.ticket), _('Latest comments for ticket #%d') % self.ticket.pk)

    def test_feed_link(self):
        """
        Test the ``link`` method of the feed.
        """
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.link(self.ticket), self.ticket.get_absolute_url())

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.feed_url(self.ticket), self.ticket.get_latest_comments_rss_feed_url())

    def test_feed_description(self):
        """
        Test the ``description`` method of the feed.
        """
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.description(self.ticket), _('Latest comments for ticket #%d') % self.ticket.pk)

    def test_author_name(self):
        """
        Test the base ``author_name`` method.
        """
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(self.ticket.submitter.username, feed.author_name(self.ticket))

    def test_author_name_anonymous(self):
        """
        Test the base ``author_name`` method with an inactive user.
        """
        self.ticket.submitter.is_active = False
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(_('Anonymous'), feed.author_name(self.ticket))

    def test_categories(self):
        """
        Test the base ``categories`` method.
        """
        component = AppComponent.objects.create(name='test',
                                                internal_name='test-app',
                                                description='Test component')
        self.ticket.component = component
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.categories(self.ticket),
                         (self.ticket.component.name, self.ticket.status, self.ticket.priority, self.ticket.difficulty))

    def test_categories_no_component(self):
        """
        Test the base ``categories`` method.
        """
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.categories(self.ticket),
                         (self.ticket.status, self.ticket.priority, self.ticket.difficulty))

    def test_feed_items(self):
        """
        Test the items returned by the ``items`` method of the feed.
        """
        comment = IssueComment.objects.create(issue=self.ticket,
                                              author=self.user,
                                              body='Test comment')
        self.assertIsNotNone(comment)

        feed = LatestTicketCommentsForIssueFeed()
        queryset = feed.items(self.ticket)
        self.assertQuerysetEqual(queryset, ['<IssueComment: Comment for issue "Test ticket": "Test comment\n\n...">'])

    def test_items_limit(self):
        """
        Test if only the N most recent tickets are included in the feed.
        """
        comments = []
        for i in range(NB_COMMENTS_IN_RECENT_COMMENT_FEED + 5):
            obj = IssueComment.objects.create(issue=self.ticket,
                                              author=self.user,
                                              body='Test comment')
            comments.append(repr(obj))

        # Test the object in the feed
        feed = LatestTicketCommentsForIssueFeed()
        items = feed.items(self.ticket)
        self.assertQuerysetEqual(items, comments[:NB_COMMENTS_IN_RECENT_COMMENT_FEED])

    def test_item_title(self):
        """
        Test the base ``item_title`` method.
        """
        item = MagicMock()
        item.issue = MagicMock(title='Test')
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(item.issue.title, feed.item_title(item))

    def test_item_description(self):
        """
        Test the base ``item_description`` method.
        """
        item = MagicMock(body_html='Test')
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(item.body_html, feed.item_description(item))

    def test_item_author_name(self):
        """
        Test the base ``item_author_name`` method.
        """
        item = MagicMock()
        item.author = MagicMock(username='Johndoe', is_active=True)
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(item.author.username, feed.item_author_name(item))

    def test_item_author_name_anonymous(self):
        """
        Test the base ``item_author_name`` method with an inactive user.
        """
        item = MagicMock()
        item.author = MagicMock(username='Johndoe', is_active=False)
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(_('Anonymous'), feed.item_author_name(item))

    def test_item_pubdate(self):
        """
        Test the base ``item_pubdate`` method.
        """
        item = MagicMock(pub_date=timezone.now())
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(item.pub_date, feed.item_pubdate(item))

    def test_item_updateddate(self):
        """
        Test the base ``item_updateddate`` method.
        """
        item = MagicMock(last_modification_date=timezone.now())
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(item.last_modification_date, feed.item_updateddate(item))


class LatestTicketCommentsForIssueAtomFeedTestCase(SimpleTestCase):
    """
    Tests suite for the ``LatestTicketCommentsForIssueAtomFeed`` feed class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        self.assertEqual(LatestTicketCommentsForIssueAtomFeed.feed_type, Atom1Feed)
        self.assertEqual(LatestTicketCommentsForIssueAtomFeed.title, LatestTicketCommentsForIssueFeed.title)
        self.assertEqual(LatestTicketCommentsForIssueAtomFeed.link, LatestTicketCommentsForIssueFeed.link)
        self.assertEqual(LatestTicketCommentsForIssueAtomFeed.subtitle, LatestTicketCommentsForIssueFeed.description)

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket',
                                            description='Test',
                                            submitter=user,
                                            assigned_to=user)

        # Test the method
        feed = LatestTicketCommentsForIssueFeed()
        self.assertEqual(feed.feed_url(ticket), ticket.get_latest_comments_atom_feed_url())
