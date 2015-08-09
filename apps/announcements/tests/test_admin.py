"""
Tests suite for the admin views of the announcements app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import Announcement


class AnnouncementAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_superuser(username='johndoe',
                                                                password='illpassword',
                                                                email='john.doe@example.com')
        # Unpublished announcement
        self.announcement = Announcement.objects.create(title='Test 1',
                                                        slug='test-1',
                                                        author=self.author,
                                                        content='Hello World!')

    def test_announcement_list_view_available(self):
        """
        Test the availability of the "announcement list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:announcements_announcement_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_announcement_edit_view_available(self):
        """
        Test the availability of the "edit announcement" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:announcements_announcement_change', args=[self.announcement.pk]))
        self.assertEqual(response.status_code, 200)
