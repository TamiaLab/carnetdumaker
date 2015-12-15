"""
Tests suite for the admin views of the notifications app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import Notification


class NotificationAdminTestCase(TestCase):
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
        self.notification = Notification.objects.create(recipient=self.author,
                                                        title='Test',
                                                        message='Test',
                                                        message_html='Test')

    def test_notification_list_view_available(self):
        """
        Test the availability of the "notification list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:notifications_notification_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_notification_edit_view_available(self):
        """
        Test the availability of the "edit notification" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:notifications_notification_change', args=[self.notification.pk]))
        self.assertEqual(response.status_code, 200)


class NotificationUserProfileAdminTestCase(TestCase):
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
        self.notification_profile = self.author.notifications_profile

    def test_notification_list_view_available(self):
        """
        Test the availability of the "notifications profile list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:notifications_notificationsuserprofile_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_notification_edit_view_available(self):
        """
        Test the availability of the "edit notifications profile" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:notifications_notificationsuserprofile_change',
                                      args=[self.notification_profile.pk]))
        self.assertEqual(response.status_code, 200)
