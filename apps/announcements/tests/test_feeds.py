"""
Tests suite for the feeds of the announcements app.
"""

from datetime import timedelta

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from ..models import (Announcement,
                      AnnouncementTag)
from ..feeds import (LatestAnnouncementsFeed,
                     LatestAnnouncementsAtomFeed,
                     LatestAnnouncementsForTagFeed,
                     LatestAnnouncementsForTagAtomFeed)
from ..settings import NB_ANNOUNCEMENTS_PER_FEED


class LatestAnnouncementsFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestAnnouncementsFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.title, _('Latest announcements'))
        self.assertEqual(feed.link, reverse('announcements:index'))
        self.assertEqual(feed.feed_url, reverse('announcements:latest_announcements_rss'))
        self.assertEqual(feed.description, _('Latest announcements'))

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        past_now = now - timedelta(seconds=1)
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement_unpublished = Announcement.objects.create(title='Test 1',
                                                               slug='test-1',
                                                               author=author,
                                                               content='Hello World!',
                                                               pub_date=None)
        announcement_published = Announcement.objects.create(title='Test 2',
                                                             slug='test-2',
                                                             author=author,
                                                             content='Hello World!',
                                                             pub_date=past_now)
        announcement_published_in_future = Announcement.objects.create(title='Test 3',
                                                                       slug='test-3',
                                                                       author=author,
                                                                       content='Hello World!',
                                                                       pub_date=future_now)
        announcement_published_site_wide = Announcement.objects.create(title='Test 4',
                                                                       slug='test-4',
                                                                       author=author,
                                                                       content='Hello World!',
                                                                       pub_date=now,
                                                                       site_wide=True)
        self.assertIsNotNone(announcement_unpublished)
        self.assertIsNotNone(announcement_published)
        self.assertIsNotNone(announcement_published_in_future)
        self.assertIsNotNone(announcement_published_site_wide)

        # Test the resulting feed content
        feed = LatestAnnouncementsFeed()
        items = feed.items()
        self.assertQuerysetEqual(items, ['<Announcement: Test 4>', '<Announcement: Test 2>'])

    def test_items_limit(self):
        """
        Test if only the N most recent announcements are included in the feed.
        """
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcements = []
        for i in range(NB_ANNOUNCEMENTS_PER_FEED + 5):
            pub_date = now - timedelta(seconds=i)
            obj = Announcement.objects.create(title='Test %d' % i,
                                              slug='test-%d' % i,
                                              author=author,
                                              content='Hello World!',
                                              pub_date=pub_date)
            announcements.append(repr(obj))

        # Test the object in the feed
        feed = LatestAnnouncementsFeed()
        items = feed.items()
        self.assertQuerysetEqual(items, announcements[:NB_ANNOUNCEMENTS_PER_FEED])

    def test_item_title(self):
        """
        Test the ``item_title`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_title(announcement), announcement.title)

    def test_item_description(self):
        """
        Test the ``item_description`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_description(announcement), announcement.content_html)

    def test_item_author_name(self):
        """
        Test the ``item_author_name`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_author_name(announcement), announcement.author.username)

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
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_author_name(announcement), _('Anonymous'))

    def test_item_pubdate(self):
        """
        Test the ``item_pubdate`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)

        # Test the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_pubdate(announcement), announcement.pub_date)

    def test_item_updateddate(self):
        """
        Test the ``item_updateddate`` method of the feed with an announcement modified after being published.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)
        announcement.title = 'Test 1 - reborn'
        announcement.save()
        self.assertIsNotNone(announcement.last_content_modification_date)
        self.assertIsNotNone(announcement.pub_date)

        # Test the result of the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_updateddate(announcement), announcement.last_content_modification_date)

    def test_item_updateddate_no_modification(self):
        """
        Test the ``item_updateddate`` method of the feed with an announcement never modified.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)
        self.assertIsNone(announcement.last_content_modification_date)
        self.assertIsNotNone(announcement.pub_date)

        # Test the result of the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_updateddate(announcement), announcement.pub_date)

    def test_item_categories(self):
        """
        Test the ``item_categories`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)
        self.assertIsNone(announcement.last_content_modification_date)
        self.assertIsNotNone(announcement.pub_date)

        # Add some tags
        tag1 = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')
        tag2 = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')
        announcement.tags.add(tag1)
        announcement.tags.add(tag2)

        # Test the result of the method
        feed = LatestAnnouncementsFeed()
        self.assertEqual(feed.item_categories(announcement), ['Tag 1', 'Tag 1'])


class LatestAnnouncementsAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestAnnouncementsAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestAnnouncementsAtomFeed()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.title, LatestAnnouncementsFeed.title)
        self.assertEqual(feed.link, LatestAnnouncementsFeed.link)
        self.assertEqual(feed.feed_url, reverse('announcements:latest_announcements_atom'))
        self.assertEqual(feed.subtitle, LatestAnnouncementsFeed.description)


class LatestAnnouncementsForTagFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestAnnouncementsForTagFeed`` class.
    """

    def test_feed_get_object(self):
        """
        Test the ``get_object`` method of the feed.
        """

        # Create some test fixtures
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.get_object(None, slug='tag-1'), tag)

    def test_feed_title(self):
        """
        Test the ``title`` method of the feed.
        """

        # Create some test fixtures
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.title(tag), _('Latest announcements with tag "%s"') % tag.name)

    def test_feed_link(self):
        """
        Test the ``link`` method of the feed.
        """

        # Create some test fixtures
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.link(tag), tag.get_absolute_url())

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.feed_url(tag), tag.get_latest_announcements_rss_feed_url())

    def test_feed_description(self):
        """
        Test the ``description`` method of the feed.
        """

        # Create some test fixtures
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.description(tag), _('Latest announcements with tag "%s"') % tag.name)

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        past_now = now - timedelta(seconds=1)
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement_unpublished = Announcement.objects.create(title='Test 1',
                                                               slug='test-1',
                                                               author=author,
                                                               content='Hello World!',
                                                               pub_date=None)
        announcement_published = Announcement.objects.create(title='Test 2',
                                                             slug='test-2',
                                                             author=author,
                                                             content='Hello World!',
                                                             pub_date=past_now)
        announcement_published_in_future = Announcement.objects.create(title='Test 3',
                                                                       slug='test-3',
                                                                       author=author,
                                                                       content='Hello World!',
                                                                       pub_date=future_now)
        announcement_published_site_wide = Announcement.objects.create(title='Test 4',
                                                                       slug='test-4',
                                                                       author=author,
                                                                       content='Hello World!',
                                                                       pub_date=now,
                                                                       site_wide=True)
        self.assertIsNotNone(announcement_unpublished)
        self.assertIsNotNone(announcement_published)
        self.assertIsNotNone(announcement_published_in_future)
        self.assertIsNotNone(announcement_published_site_wide)

        # Add some tests tags
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')
        announcement_published.tags.add(tag)
        tag2 = AnnouncementTag.objects.create(name='Tag 2', slug='tag-2')
        announcement_published_site_wide.tags.add(tag2)

        # Test the resulting feed content
        feed = LatestAnnouncementsForTagFeed()
        items = feed.items(tag)
        self.assertQuerysetEqual(items, ['<Announcement: Test 2>'])

    def test_items_limit(self):
        """
        Test if only the N most recent announcements are included in the feed.
        """
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')
        announcements = []
        for i in range(NB_ANNOUNCEMENTS_PER_FEED + 5):
            pub_date = now - timedelta(seconds=i)
            obj = Announcement.objects.create(title='Test %d' % i,
                                              slug='test-%d' % i,
                                              author=author,
                                              content='Hello World!',
                                              pub_date=pub_date)
            obj.tags.add(tag)
            announcements.append(repr(obj))

        # Test the object in the feed
        feed = LatestAnnouncementsForTagFeed()
        items = feed.items(tag)
        self.assertQuerysetEqual(items, announcements[:NB_ANNOUNCEMENTS_PER_FEED])

    def test_item_title(self):
        """
        Test the ``item_title`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_title(announcement), announcement.title)

    def test_item_description(self):
        """
        Test the ``item_description`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_description(announcement), announcement.content_html)

    def test_item_author_name(self):
        """
        Test the ``item_author_name`` method of the feed.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_author_name(announcement), announcement.author.username)

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
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_author_name(announcement), _('Anonymous'))

    def test_item_pubdate(self):
        """
        Test the ``item_pubdate`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)

        # Test the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_pubdate(announcement), announcement.pub_date)

    def test_item_updateddate(self):
        """
        Test the ``item_updateddate`` method of the feed with an announcement modified after being published.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)
        announcement.title = 'Test 1 - reborn'
        announcement.save()
        self.assertIsNotNone(announcement.last_content_modification_date)
        self.assertIsNotNone(announcement.pub_date)

        # Test the result of the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_updateddate(announcement), announcement.last_content_modification_date)

    def test_item_updateddate_no_modification(self):
        """
        Test the ``item_updateddate`` method of the feed with an announcement never modified.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)
        self.assertIsNone(announcement.last_content_modification_date)
        self.assertIsNotNone(announcement.pub_date)

        # Test the result of the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_updateddate(announcement), announcement.pub_date)

    def test_item_categories(self):
        """
        Test the ``item_categories`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)
        self.assertIsNone(announcement.last_content_modification_date)
        self.assertIsNotNone(announcement.pub_date)

        # Add some tags
        tag1 = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')
        tag2 = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')
        announcement.tags.add(tag1)
        announcement.tags.add(tag2)

        # Test the result of the method
        feed = LatestAnnouncementsForTagFeed()
        self.assertEqual(feed.item_categories(announcement), ['Tag 1', 'Tag 1'])


class LatestAnnouncementsForTagAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestAnnouncementsForTagAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        self.assertEqual(LatestAnnouncementsForTagAtomFeed.feed_type, Atom1Feed)
        self.assertEqual(LatestAnnouncementsForTagAtomFeed.title, LatestAnnouncementsForTagFeed.title)
        self.assertEqual(LatestAnnouncementsForTagAtomFeed.link, LatestAnnouncementsForTagFeed.link)
        self.assertEqual(LatestAnnouncementsForTagAtomFeed.subtitle, LatestAnnouncementsForTagFeed.description)

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        tag = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')

        # Test the method
        feed = LatestAnnouncementsForTagAtomFeed()
        self.assertEqual(feed.feed_url(tag), tag.get_latest_announcements_atom_feed_url())
