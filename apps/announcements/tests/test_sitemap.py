"""
Tests suite for the sitemap of the announcements app.
"""

from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import (Announcement,
                      AnnouncementTag)
from ..sitemap import (AnnouncementsSitemap,
                       AnnouncementTagsSitemap)


class AnnouncementsSitemapTestCase(TestCase):
    """
    Tests suite for the ``AnnouncementsSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
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

        # Test the resulting sitemap content
        sitemap = AnnouncementsSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<Announcement: Test 4>', '<Announcement: Test 2>'])

    def test_lastmod(self):
        """
        Test the ``lastmod`` method of the sitemap with an announcement modified after being published.
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
        sitemap = AnnouncementsSitemap()
        self.assertEqual(sitemap.lastmod(announcement), announcement.last_content_modification_date)

    def test_lastmod_no_modification(self):
        """
        Test the ``lastmod`` method of the sitemap with an announcement never modified.
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
        sitemap = AnnouncementsSitemap()
        self.assertEqual(sitemap.lastmod(announcement), announcement.pub_date)


class AnnouncementTagsSitemapTestCase(TestCase):
    """
    Tests suite for the ``AnnouncementTagsSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        tag1 = AnnouncementTag.objects.create(name='Tag 1', slug='tag-1')
        tag2 = AnnouncementTag.objects.create(name='Tag 2', slug='tag-2')
        tag3 = AnnouncementTag.objects.create(name='Tag 3', slug='tag-3')
        self.assertIsNotNone(tag1)
        self.assertIsNotNone(tag2)
        self.assertIsNotNone(tag3)

        # Test the resulting sitemap content
        sitemap = AnnouncementTagsSitemap()
        items = list(sitemap.items())
        self.assertEqual(3, len(items))
        self.assertEqual(items, [tag1, tag2, tag3])
