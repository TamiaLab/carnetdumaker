"""
Tests suite for the template tags of the announcements app.
"""

from datetime import timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..templatetags.announcements import (recent_announcements,
                                          recent_announcements_list,
                                          global_announcements,
                                          global_announcements_list)
from ..models import Announcement


class AnnouncementTemplateTagsTestCase(TestCase):
    """
    Tests case for all template tags of the announcements app.
    """

    def setUp(self):
        """
        Create a test user named "Johndoe".
        """
        now = timezone.now()
        past_now = now - timedelta(minutes=1)
        past_now2 = now - timedelta(minutes=2)
        future_now = now + timedelta(minutes=10)
        self.user = get_user_model().objects.create_user(username='johndoe',
                                                         password='illpassword',
                                                         email='johndoe@example.com')
        self.a1 = Announcement.objects.create(title='Announcement 1',
                                              slug='announcement-1',
                                              author=self.user,
                                              pub_date=None,
                                              content='Announcement 1')
        self.a2 = Announcement.objects.create(title='Announcement 2',
                                              slug='announcement-2',
                                              author=self.user,
                                              pub_date=now,
                                              content='Announcement 2')
        self.a3 = Announcement.objects.create(title='Announcement 3',
                                              slug='announcement-3',
                                              author=self.user,
                                              pub_date=past_now,
                                              content='Announcement 3')
        self.a4 = Announcement.objects.create(title='Announcement 4',
                                              slug='announcement-4',
                                              author=self.user,
                                              pub_date=past_now2,
                                              site_wide=True,
                                              content='Announcement 4')
        self.a5 = Announcement.objects.create(title='Announcement 5',
                                              slug='announcement-5',
                                              author=self.user,
                                              pub_date=future_now,
                                              content='Announcement 5')

    def test_recent_announcements(self):
        """
        Test if the ``recent_announcements`` template tag work as expected.
        """
        announcements = recent_announcements(5)
        self.assertIn('announcements', announcements)
        self.assertQuerysetEqual(announcements['announcements'], ['<Announcement: Announcement 2>',
                                                                  '<Announcement: Announcement 3>',
                                                                  '<Announcement: Announcement 4>'])

    def test_recent_announcements_list(self):
        """
        Test if the ``recent_announcements_list`` template tag work as expected.
        """
        announcements = recent_announcements_list(5)
        self.assertQuerysetEqual(announcements, ['<Announcement: Announcement 2>',
                                                 '<Announcement: Announcement 3>',
                                                 '<Announcement: Announcement 4>'])

    def test_global_announcements(self):
        """
        Test if the ``global_announcements`` template tag work as expected.
        """
        announcements = global_announcements()
        self.assertIn('announcements', announcements)
        self.assertQuerysetEqual(announcements['announcements'], ['<Announcement: Announcement 4>'])

    def test_global_announcements_list(self):
        """
        Test if the ``global_announcements_list`` template tag work as expected.
        """
        announcements = global_announcements_list()
        self.assertQuerysetEqual(announcements, ['<Announcement: Announcement 4>'])
