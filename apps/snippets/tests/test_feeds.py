"""
Tests suite for the feeds of the code snippets app.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from ..models import CodeSnippet
from ..feeds import (LatestCodeSnippetsFeed,
                     LatestCodeSnippetsAtomFeed)
from ..settings import NB_SNIPPETS_PER_FEED


class LatestCodeSnippetsFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestCodeSnippetsFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.title, _('Latest code snippets'))
        self.assertEqual(feed.link, reverse('snippets:index'))
        self.assertEqual(feed.feed_url, reverse('snippets:latest_snippets_rss'))
        self.assertEqual(feed.description, _('Latest code snippets'))

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        CodeSnippet.objects.create(title='Code 1',
                                   author=author,
                                   filename='helloworld.py',
                                   description='Hello World written in Python 3',
                                   source_code='print("Hello World!")\n')
        CodeSnippet.objects.create(title='Code 2',
                                   author=author,
                                   filename='helloworld.py',
                                   description='Hello World written in Python 3',
                                   source_code='print("Hello World!")\n')
        CodeSnippet.objects.create(title='Code 3',
                                   author=author,
                                   filename='helloworld.py',
                                   description='Hello World written in Python 3',
                                   source_code='print("Hello World!")\n')

        # Test the resulting feed content
        feed = LatestCodeSnippetsFeed()
        items = feed.items()
        self.assertQuerysetEqual(items, ['<CodeSnippet: Code 3>',
                                         '<CodeSnippet: Code 2>',
                                         '<CodeSnippet: Code 1>'])

    def test_items_limit(self):
        """
        Test if only the N most recent code snippets are included in the feed.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippets = []
        for i in range(NB_SNIPPETS_PER_FEED + 5):
            obj = CodeSnippet.objects.create(title='Code %d' % i,
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')
            snippets.append(repr(obj))
        snippets = list(reversed(snippets))

        # Test the object in the feed
        feed = LatestCodeSnippetsFeed()
        items = feed.items()
        self.assertQuerysetEqual(items, snippets[:NB_SNIPPETS_PER_FEED])

    def test_item_title(self):
        """
        Test the ``item_title`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')

        # Test the method
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.item_title(snippet), snippet.title)

    def test_item_description(self):
        """
        Test the ``item_description`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')

        # Test the method
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.item_description(snippet),
                         '<style>\n%s\n</style>\n%s' % (snippet.css_for_display, snippet.html_for_display))

    def test_item_author_name(self):
        """
        Test the ``item_author_name`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')

        # Test the method
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.item_author_name(snippet), snippet.author.username)

    def test_item_author_name_anonymous(self):
        """
        Test the ``item_author_name`` method of the feed with an author not active.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        author.is_active = False
        author.save()
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')

        # Test the method
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.item_author_name(snippet), _('Anonymous'))

    def test_item_pubdate(self):
        """
        Test the ``item_pubdate`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')

        # Test the method
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.item_pubdate(snippet), snippet.creation_date)

    def test_item_updateddate(self):
        """
        Test the ``item_updateddate`` method of the feed with an code snippet modified after being published.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')
        snippet.title = 'Code 1 - reborn'
        snippet.save()
        self.assertIsNotNone(snippet.last_modification_date)
        self.assertIsNotNone(snippet.creation_date)

        # Test the result of the method
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.item_updateddate(snippet), snippet.last_modification_date)

    def test_item_updateddate_no_modification(self):
        """
        Test the ``item_updateddate`` method of the feed with an code snippet never modified.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')
        self.assertIsNone(snippet.last_modification_date)
        self.assertIsNotNone(snippet.creation_date)

        # Test the result of the method
        feed = LatestCodeSnippetsFeed()
        self.assertEqual(feed.item_updateddate(snippet), snippet.creation_date)


class LatestCodeSnippetsAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestCodeSnippetsAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestCodeSnippetsAtomFeed()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.title, LatestCodeSnippetsFeed.title)
        self.assertEqual(feed.link, LatestCodeSnippetsFeed.link)
        self.assertEqual(feed.feed_url, reverse('snippets:latest_snippets_atom'))
        self.assertEqual(feed.subtitle, LatestCodeSnippetsFeed.description)
