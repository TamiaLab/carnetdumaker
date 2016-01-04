"""
Tests suite for the models of the announcements app.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from ..models import (Announcement,
                      AnnouncementTag,
                      AnnouncementTwitterCrossPublication)
from ..constants import ANNOUNCEMENTS_TYPE_DEFAULT


class AnnouncementTestCase(TestCase):
    """
    Tests suite for the ``Announcement`` data model.
    """

    def _get_announcement(self):
        """
        Create a new unpublished announcement with only required fields (title, slug, author, content).
        :return: The newly created announcement.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')
        return announcement

    def test_default_values(self):
        """
        Test default values of the newly created announcement.
        """
        announcement = self._get_announcement()
        self.assertIsNotNone(announcement.creation_date)
        self.assertIsNone(announcement.last_content_modification_date)
        self.assertIsNone(announcement.pub_date)
        self.assertEqual(announcement.type, ANNOUNCEMENTS_TYPE_DEFAULT)
        self.assertFalse(announcement.site_wide)
        self.assertTrue(Announcement.objects.use_for_related_fields)

    def test_str_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        announcement = self._get_announcement()
        self.assertEqual(announcement.title, str(announcement))

    def test_get_absolute_url_method(self):
        """
        Test ``get_absolute_url`` method with a valid announcement.
        """
        announcement = self._get_announcement()
        excepted_url = reverse('announcements:announcement_detail', kwargs={'slug': announcement.slug})
        self.assertEqual(excepted_url, announcement.get_absolute_url())

    def test_is_modified_after_content_change(self):
        """
        Test if the object is flagged has "changed" when the content text is altered (should).
        """
        announcement = self._get_announcement()
        announcement.pub_date = timezone.now()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.content = 'New content'
        announcement.save()
        self.assertTrue(announcement.has_been_modified_after_publication())

    def test_is_modified_after_title_change(self):
        """
        Test if the object is flagged has "changed" when the title is altered (should).
        """
        announcement = self._get_announcement()
        announcement.pub_date = timezone.now()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.title = 'New title'
        announcement.save()
        self.assertTrue(announcement.has_been_modified_after_publication())

    def test_is_NOT_modified_after_other_change(self):
        """
        Test if the object is flagged has "changed" when something else than the
        content text or title is altered (should NOT).
        """
        new_author = get_user_model().objects.create_user(username='jonhsmith',
                                                          password='jonhsmith',
                                                          email='jonh.smith@example.com')
        announcement = self._get_announcement()
        announcement.pub_date = timezone.now()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.slug = 'new-slug'
        announcement.save()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.author = new_author
        announcement.save()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.pub_date = timezone.now()
        announcement.save()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.type = 'new-type'
        announcement.save()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.site_wide = True
        announcement.save()
        self.assertFalse(announcement.has_been_modified_after_publication())
        announcement.content_html = '<p>New raw content<p>'
        announcement.save()
        self.assertFalse(announcement.has_been_modified_after_publication())

    def test_fix_last_content_modification_on_publish(self):
        """
        Test if the ``last_content_modification_date`` is fixed when before the ``pub_date``.
        """
        announcement = self._get_announcement()
        now = timezone.now()
        announcement.pub_date = now
        announcement.last_content_modification_date = now - timedelta(seconds=1)
        announcement.save()
        self.assertIsNone(announcement.last_content_modification_date)

    def test_fix_last_content_modification_on_publish_2(self):
        """
        Test if the ``last_content_modification_date`` is fixed when at ``pub_date``.
        """
        announcement = self._get_announcement()
        now = timezone.now()
        announcement.pub_date = now
        announcement.last_content_modification_date = now
        announcement.save()
        self.assertIsNone(announcement.last_content_modification_date)

    def test_no_fix_last_content_modification_on_future_modification(self):
        """
        Test if the ``last_content_modification_date`` is NOT fixed when after than the ``pub_date``.
        """
        announcement = self._get_announcement()
        now = timezone.now()
        future_now = now + timedelta(seconds=1)
        announcement.pub_date = now
        announcement.last_content_modification_date = future_now
        announcement.save()
        self.assertEqual(announcement.last_content_modification_date, future_now)

    def test_fix_last_content_modification_not_published(self):
        """
        Test if the ``last_content_modification_date`` is fixed when ``pub_date`` is not set.
        """
        announcement = self._get_announcement()
        now = timezone.now()
        announcement.pub_date = None
        announcement.last_content_modification_date = now
        announcement.save()
        self.assertIsNone(announcement.last_content_modification_date)

    def test_slug_conflict_resolution(self):
        """
        Test if the ``save`` method fix slug conflict.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement_1 = Announcement.objects.create(title='Test 1',
                                                     slug='test-1',
                                                     author=author,
                                                     content='Hello World!')
        announcement_2 = Announcement.objects.create(title='Test 2',
                                                     slug='test-1',
                                                     author=author,
                                                     content='Hello World!')
        announcement_3 = Announcement.objects.create(title='Test 2',
                                                     slug='test-1',
                                                     author=author,
                                                     content='Hello World!')
        self.assertNotEqual(announcement_1.slug, announcement_2.slug)
        self.assertNotEqual(announcement_2.slug, announcement_3.slug)
        self.assertNotEqual(announcement_1.slug, announcement_3.slug)

    def test_is_published_with_unpublished_announcement(self):
        """
        Test the ``is_published()`` method with an unpublished announcement.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=None)
        self.assertIsNone(announcement.pub_date)
        self.assertFalse(announcement.is_published())

    def test_is_published_with_published_announcement(self):
        """
        Test the ``is_published()`` method with a published announcement.
        """
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now)
        self.assertEqual(announcement.pub_date, now)
        self.assertTrue(announcement.is_published())

    def test_is_published_with_published_in_future_announcement(self):
        """
        Test the ``is_published()`` method with a announcement published in future.
        """
        future_now = timezone.now() + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=future_now)
        self.assertEqual(announcement.pub_date, future_now)
        self.assertFalse(announcement.is_published())

    def test_can_see_preview_with_author(self):
        """
        Test the ``can_see_preview()`` method with the announcement author itself.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')
        self.assertEqual(announcement.author, author)
        self.assertTrue(announcement.can_see_preview(author))

    def test_can_see_preview_anonymous(self):
        """
        Test the ``can_see_preview()`` method with a random user (not author, nor authorized to see preview).
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        user = get_user_model().objects.create_user(username='anonuser',
                                                      password='anonuser',
                                                      email='anon.user@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')
        self.assertEqual(announcement.author, author)
        self.assertFalse(announcement.can_see_preview(user))

    def test_can_see_preview_with_authorized_user(self):
        """
        Test the ``can_see_preview()`` method with an authorized user.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        authorized_user = get_user_model().objects.create_user(username='jonhsmith',
                                                               password='jonhsmith',
                                                               email='jonh.smith@example.com')
        content_type = ContentType.objects.get_for_model(Announcement)
        permission = Permission.objects.get(codename='can_see_preview', content_type=content_type)
        authorized_user.user_permissions.add(permission)
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')
        self.assertNotEqual(announcement.author, authorized_user)
        self.assertTrue(announcement.can_see_preview(authorized_user))

    def test_published_and_published_site_wide(self):
        """
        Test the ``published`` and ``published_site_wide`` methods of the ``AnnouncementManager`` class.
        """
        now = timezone.now()
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
                                                             pub_date=now)
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

        queryset_published = Announcement.objects.published()
        self.assertEqual(len(queryset_published), 2)
        self.assertNotIn(announcement_unpublished, queryset_published)
        self.assertIn(announcement_published, queryset_published)
        self.assertIn(announcement_published_site_wide, queryset_published)
        self.assertNotIn(announcement_published_in_future, queryset_published)

        queryset_published_site_wide = Announcement.objects.published_site_wide()
        self.assertEqual(len(queryset_published_site_wide), 1)
        self.assertNotIn(announcement_unpublished, queryset_published_site_wide)
        self.assertNotIn(announcement_published, queryset_published_site_wide)
        self.assertIn(announcement_published_site_wide, queryset_published_site_wide)
        self.assertNotIn(announcement_published_in_future, queryset_published_site_wide)

    def test_published_and_published_site_wide_order_by(self):
        """
        Test the ``published`` and ``published_site_wide`` methods of the ``AnnouncementManager`` class.
        """
        now = timezone.now()
        now_m1 = now - timedelta(seconds=1)
        now_m2 = now - timedelta(seconds=2)
        now_m3 = now - timedelta(seconds=3)
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        Announcement.objects.create(title='Test 1',
                                    slug='test-1',
                                    author=author,
                                    content='Hello World!',
                                    pub_date=now_m3,
                                    site_wide=True)
        Announcement.objects.create(title='Test 2',
                                    slug='test-2',
                                    author=author,
                                    content='Hello World!',
                                    pub_date=now_m2,
                                    site_wide=True)
        Announcement.objects.create(title='Test 3',
                                    slug='test-3',
                                    author=author,
                                    content='Hello World!',
                                    pub_date=now_m1,
                                    site_wide=True)
        Announcement.objects.create(title='Test 4',
                                    slug='test-4',
                                    author=author,
                                    content='Hello World!',
                                    pub_date=now,
                                    site_wide=True)

        # Test the two queryset order
        queryset_published = Announcement.objects.published()
        self.assertQuerysetEqual(queryset_published, ['<Announcement: Test 4>',
                                                      '<Announcement: Test 3>',
                                                      '<Announcement: Test 2>',
                                                      '<Announcement: Test 1>'])
        queryset_published_site_wide = Announcement.objects.published_site_wide()
        self.assertQuerysetEqual(queryset_published_site_wide, ['<Announcement: Test 4>',
                                                                '<Announcement: Test 3>',
                                                                '<Announcement: Test 2>',
                                                                '<Announcement: Test 1>'])


class AnnouncementTagTestCase(TestCase):
    """
    Tests suite for the ``AnnouncementTag`` data model.
    """

    def test_str_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        tag = AnnouncementTag.objects.create(name='test', slug='test')
        self.assertEqual(tag.name, str(tag))

    def test_get_absolute_url_method(self):
        """
        Test ``get_absolute_url`` method with a valid announcement.
        """
        tag = AnnouncementTag.objects.create(name='test', slug='test')
        excepted_url = reverse('announcements:tag_detail', kwargs={'slug': tag.slug})
        self.assertEqual(excepted_url, tag.get_absolute_url())

    def test_get_latest_announcements_rss_feed_url_method(self):
        """
        Test ``get_latest_announcements_rss_feed_url`` method with a valid announcement.
        """
        tag = AnnouncementTag.objects.create(name='test', slug='test')
        excepted_url = reverse('announcements:latest_tag_announcements_rss', kwargs={'slug': tag.slug})
        self.assertEqual(excepted_url, tag.get_latest_announcements_rss_feed_url())

    def test_get_latest_announcements_atom_feed_url_method(self):
        """
        Test ``get_latest_announcements_atom_feed_url`` method with a valid announcement.
        """
        tag = AnnouncementTag.objects.create(name='test', slug='test')
        excepted_url = reverse('announcements:latest_tag_announcements_atom', kwargs={'slug': tag.slug})
        self.assertEqual(excepted_url, tag.get_latest_announcements_atom_feed_url())


class AnnouncementTwitterCrossPublicationTestCase(TestCase):
    """
    Tests suite for the ``AnnouncementTwitterCrossPublication`` data model.
    """

    def test_str_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        announcement = Announcement.objects.create(title='Test 1',
                                                   slug='test-1',
                                                   author=author,
                                                   content='Hello World!')
        tweet = AnnouncementTwitterCrossPublication.objects.create(announcement=announcement,
                                                                   tweet_id='0123456789')
        self.assertEqual('%s -> %s' % (announcement, '0123456789'), str(tweet))

    def test_publish_pending_announcements(self):
        """
        Test the ``publish_pending_announcements`` method of the manager.
        """

        # Create some test fixtures
        now = timezone.now()
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
                                                             pub_date=now)
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

        with patch('apps.announcements.managers.publish_announcement_on_twitter') as mock:
            mock.return_value = '0123456789'
            AnnouncementTwitterCrossPublication.objects.publish_pending_announcements()

        self.assertEqual(2, mock.call_count)
        mock.assert_any_call(announcement_published)
        mock.assert_any_call(announcement_published_site_wide)

        tweets = AnnouncementTwitterCrossPublication.objects.all()
        self.assertQuerysetEqual(tweets, ['<AnnouncementTwitterCrossPublication: Test 4 -> 0123456789>',
                                          '<AnnouncementTwitterCrossPublication: Test 2 -> 0123456789>'])

    def test_publish_pending_announcements_error(self):
        """
        Test the ``publish_pending_announcements`` method of the manager when the Twitter api fail.
        """

        # Create some test fixtures
        now = timezone.now()
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
                                                             pub_date=now)
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

        with patch('apps.announcements.managers.publish_announcement_on_twitter') as mock:
            mock.return_value = False
            AnnouncementTwitterCrossPublication.objects.publish_pending_announcements()

        self.assertEqual(2, mock.call_count)
        mock.assert_any_call(announcement_published)
        mock.assert_any_call(announcement_published_site_wide)

        tweets = AnnouncementTwitterCrossPublication.objects.all()
        self.assertQuerysetEqual(tweets, [])

    def test_publish_pending_announcements_with_already_posted(self):
        """
        Test the ``publish_pending_announcements`` method of the manager when some announcements are already posted.
        """

        # Create some test fixtures
        now = timezone.now()
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
                                                             pub_date=now)
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

        AnnouncementTwitterCrossPublication.objects.create(announcement=announcement_published_site_wide,
                                                           tweet_id='0123456789')

        with patch('apps.announcements.managers.publish_announcement_on_twitter') as mock:
            mock.return_value = '0123456789'
            AnnouncementTwitterCrossPublication.objects.publish_pending_announcements()

        self.assertEqual(1, mock.call_count)
        mock.assert_any_call(announcement_published)

        tweets = AnnouncementTwitterCrossPublication.objects.all()
        print(tweets)
        self.assertQuerysetEqual(tweets, ['<AnnouncementTwitterCrossPublication: Test 2 -> 0123456789>',
                                          '<AnnouncementTwitterCrossPublication: Test 4 -> 0123456789>'])
