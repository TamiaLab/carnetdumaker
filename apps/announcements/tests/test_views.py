"""
Tests suite for the views of the announcements app.
"""

from datetime import timedelta

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import (Announcement,
                      AnnouncementTag)


class AnnouncementViewsTestCase(TestCase):
    """
    Tests case for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=1)
        future_now = now + timedelta(seconds=100)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        self.announcement_unpublished = Announcement.objects.create(title='Test 1',
                                                                    slug='test-1',
                                                                    author=author,
                                                                    content='Hello World!')
        self.announcement_published = Announcement.objects.create(title='Test 2',
                                                                  slug='test-2',
                                                                  author=author,
                                                                  content='Hello World!',
                                                                  pub_date=past_now)
        self.announcement_published = Announcement.objects.create(title='Test 3',
                                                                  slug='test-3',
                                                                  author=author,
                                                                  content='Hello World!',
                                                                  pub_date=now)
        self.announcement_published_in_future = Announcement.objects.create(title='Test 4',
                                                                            slug='test-4',
                                                                            author=author,
                                                                            content='Hello World!',
                                                                            pub_date=future_now)
        self.tag = AnnouncementTag.objects.create(name='Test tag', slug='test-tag')
        self.tag2 = AnnouncementTag.objects.create(name='Test tag 2', slug='test-tag-2')
        self.announcement_unpublished.tags.add(self.tag)
        self.announcement_published.tags.add(self.tag)
        self.announcement_published_in_future.tags.add(self.tag)

    def test_announcement_list_view_available(self):
        """
        Test the availability of the "announcement list" view.
        """
        client = Client()
        response = client.get(reverse('announcements:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'announcements/announcement_list.html')
        self.assertIn('announcements', response.context)
        self.assertQuerysetEqual(response.context['announcements'], ['<Announcement: Test 3>',
                                                                     '<Announcement: Test 2>'])

    def test_announcement_detail_view_available_with_published_announcement(self):
        """
        Test the availability of the "announcement detail" view for a published announcement.
        """
        client = Client()
        response = client.get(self.announcement_published.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'announcements/announcement_detail.html')
        self.assertIn('announcement', response.context)
        self.assertEqual(response.context['announcement'], self.announcement_published)

    def test_announcement_detail_view_unavailable_with_unpublished_announcement(self):
        """
        Test the unavailability of the "announcement detail" view for an unpublished announcement.
        """
        client = Client()
        response = client.get(self.announcement_unpublished.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_announcement_preview_available_with_unpublished_announcement_if_authorized(self):
        """
        Test the availability of the "announcement preview" view for an unpublished announcement if the
        current user is authorized to see the preview.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(self.announcement_unpublished.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'announcements/announcement_detail.html')
        self.assertIn('announcement', response.context)
        self.assertEqual(response.context['announcement'], self.announcement_unpublished)

    def test_announcement_detail_view_unavailable_with_published_in_future_announcement(self):
        """
        Test the availability of the "announcement detail" view for a published in future announcement.
        """
        client = Client()
        response = client.get(self.announcement_published_in_future.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_announcement_preview_available_with_published_in_future_announcement_if_authorized(self):
        """
        Test the availability of the "announcement preview" view for a published in future announcement if the
        current user is authorized to see the preview.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(self.announcement_published_in_future.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'announcements/announcement_detail.html')
        self.assertIn('announcement', response.context)
        self.assertEqual(response.context['announcement'], self.announcement_published_in_future)

    def test_latest_announcements_rss_feed_available(self):
        """
        Test the availability of the "latest announcements" rss feed view.
        """
        client = Client()
        response = client.get(reverse('announcements:latest_announcements_rss'))
        self.assertEqual(response.status_code, 200)

    def test_latest_announcements_atom_feed_available(self):
        """
        Test the availability of the "latest announcements" atom feed" view.
        """
        client = Client()
        response = client.get(reverse('announcements:latest_announcements_atom'))
        self.assertEqual(response.status_code, 200)

    def test_announcement_tag_list_view_available(self):
        """
        Test the availability of the "announcement tag list" view.
        """
        client = Client()
        response = client.get(reverse('announcements:tag_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'announcements/tag_list.html')
        self.assertIn('tags', response.context)
        self.assertEqual(str(response.context['tags']), str([self.tag, self.tag2]))

    def test_announcement_tag_detail_view_available(self):
        """
        Test the availability of the "announcement tag detail" view.
        """
        client = Client()
        response = client.get(reverse('announcements:tag_detail', kwargs={'slug': self.tag.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'announcements/tag_detail.html')
        self.assertIn('tag', response.context)
        self.assertEqual(response.context['tag'], self.tag)
        self.assertIn('related_announcements', response.context)
        self.assertQuerysetEqual(response.context['related_announcements'], ['<Announcement: Test 3>'])

    def test_latest_tag_announcements_rss_feed_available(self):
        """
        Test the availability of the "latest announcements for tag" rss feed view.
        """
        client = Client()
        response = client.get(reverse('announcements:latest_tag_announcements_rss', kwargs={'slug': self.tag.slug}))
        self.assertEqual(response.status_code, 200)

    def test_latest_tag_announcements_atom_feed_available(self):
        """
        Test the availability of the "latest announcements for tag" atom feed" view.
        """
        client = Client()
        response = client.get(reverse('announcements:latest_tag_announcements_atom', kwargs={'slug': self.tag.slug}))
        self.assertEqual(response.status_code, 200)
