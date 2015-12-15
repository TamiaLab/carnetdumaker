"""
Tests suite for the views of the notifications app.
"""

from django.test import TestCase, Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import Notification


class NotificationsViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create a new user named "johndoe" with password "illpassword".
        """
        self.user1 = get_user_model().objects.create_user(username='johndoe',
                                                          password='illpassword',
                                                          email='john.doe@example.com')
        self.user2 = get_user_model().objects.create_user(username='johnsmith',
                                                          password='illpassword',
                                                          email='john.smith@example.com')
        self.notif1 = Notification.objects.create(recipient=self.user1,
                                                  title='Test 1',
                                                  message='Test 1',
                                                  message_html='<p>Test 1</p>')
        self.notif2 = Notification.objects.create(recipient=self.user2,
                                                  title='Test 2',
                                                  message='Test 2',
                                                  message_html='<p>Test 2</p>')
        self.notif3 = Notification.objects.create(recipient=self.user1,
                                                  title='Test 3',
                                                  message='Test 3',
                                                  message_html='<p>Test 3</p>',
                                                  unread=False)

    def test_notifications_list_view_available(self):
        """
        Test the availability of the "notifications list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('notifications:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/notification_list.html')
        self.assertIn('notifications', response.context)
        self.assertQuerysetEqual(response.context['notifications'], ['<Notification: Test 3>',
                                                                     '<Notification: Test 1>'])

    def test_read_notifications_list_view_available(self):
        """
        Test the availability of the "read notifications list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('notifications:notification_read_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/notification_list.html')
        self.assertIn('notifications', response.context)
        self.assertQuerysetEqual(response.context['notifications'], ['<Notification: Test 3>'])

    def test_unread_notifications_list_view_available(self):
        """
        Test the availability of the "unread notifications list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('notifications:notification_unread_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/notification_list.html')
        self.assertIn('notifications', response.context)
        self.assertQuerysetEqual(response.context['notifications'], ['<Notification: Test 1>'])

    def test_notifications_list_view_redirect_not_login(self):
        """
        Test the redirection of the "notifications list" view when not logged-in.
        """
        client = Client()
        notifications_list_url = reverse('notifications:index')
        response = client.get(notifications_list_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, notifications_list_url))

    def test_mark_all_notifications_as_read_view_available(self):
        """
        Test the availability of the "mark all notifications as read" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('notifications:mark_all_as_read'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/mark_all_as_read.html')

    def test_mark_all_notifications_as_read_view_redirect_not_login(self):
        """
        Test the redirection of the "mark all notifications as read" view when not logged-in.
        """
        client = Client()
        mark_all_as_read_url = reverse('notifications:mark_all_as_read')
        response = client.get(mark_all_as_read_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, mark_all_as_read_url))

    def test_notification_detail_view_available(self):
        """
        Test the availability of the "notification detail" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(self.notif1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/notification_detail.html')
        self.assertIn('notification', response.context)
        self.assertEqual(response.context['notification'], self.notif1)

    def test_notification_detail_view_redirect_not_login(self):
        """
        Test the redirection of the "notification detail" view when not logged-in.
        """
        client = Client()
        notif_url = self.notif1.get_absolute_url()
        response = client.get(notif_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, notif_url))

    def test_notification_detail_view_unavailable_wrong_user(self):
        """
        Test the unavailability of the "notification detail" view when the current user is
        not the recipient of the given notification.
        """
        client = Client()
        client.login(username='johnsmith', password='illpassword')
        response = client.get(self.notif1.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_my_account_view_redirect_not_login(self):
        """
        Test the redirection of the "my account" view when not logged-in.
        """
        client = Client()
        myaccount_url = reverse('notifications:myaccount')
        response = client.get(myaccount_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, myaccount_url))

    def test_my_account_view_available(self):
        """
        Test the availability of the "my account" view when logged-in.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('notifications:myaccount'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications/my_account.html')
