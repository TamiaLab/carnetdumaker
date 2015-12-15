"""
Tests suite for the models of the notifications app.
"""

from unittest.mock import patch
from datetime import timedelta

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import (Notification,
                      NotificationsUserProfile)
from ..signals import (dismiss_notification,
                       unread_notification)
from ..settings import READ_NOTIFICATION_DELETION_TIMEOUT_DAYS


class NotificationTestCase(TestCase):
    """
    Tests suite for the ``Notification`` data model.
    """

    def _get_notification(self):
        """
        Create a new unread notification.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='illpassword',
                                                         email='jonh.doe@example.com')
        notification = Notification.objects.create(title='Test 1 (titre)',
                                                   message='Test 1 (msg)',
                                                   message_html='Test 1 (html)',
                                                   recipient=recipient)
        return notification

    def test_default_values(self):
        """
        Test default values of the newly created notification.
        """
        notification = self._get_notification()
        self.assertIsNotNone(notification.notification_date)
        self.assertTrue(notification.unread)
        self.assertEqual('', notification.dismiss_code)
        self.assertTrue(Notification.objects.use_for_related_fields)

    def test_str_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        notification = self._get_notification()
        self.assertEqual(notification.title, str(notification))

    def test_get_absolute_url_method(self):
        """
        Test ``get_absolute_url`` method with a valid notification.
        """
        notification = self._get_notification()
        excepted_url = reverse('notifications:notification_detail', kwargs={'pk': notification.pk})
        self.assertEqual(excepted_url, notification.get_absolute_url())

    def test_dismiss_notification_signal_on_save(self):
        """
        Test the "dismiss_notification" signal emission on model save.
        """
        notification = self._get_notification()
        signal_received = False
        received_notification = None

        def _signal_listener(sender, notification, **kwargs):
            nonlocal signal_received, received_notification
            signal_received = True
            received_notification = notification
        dismiss_notification.connect(_signal_listener)

        notification.unread = False
        notification.save()
        self.assertTrue(signal_received)
        self.assertEqual(received_notification, notification)

    def test_dismiss_notification_signal_on_save_not_trigger(self):
        """
        Test the "dismiss_notification" signal emission on model save.
        """
        notification = self._get_notification()
        signal_received = False

        def _signal_listener(sender, notification, **kwargs):
            nonlocal signal_received
            signal_received = True
        dismiss_notification.connect(_signal_listener)

        notification.unread = True
        notification.save()
        self.assertFalse(signal_received)

    def test_unread_notification_signal_on_save(self):
        """
        Test the "unread_notification" signal emission on model save.
        """
        notification = self._get_notification()
        notification.unread = False
        notification.save()

        signal_received = False
        received_notification = None

        def _signal_listener(sender, notification, **kwargs):
            nonlocal signal_received, received_notification
            signal_received = True
            received_notification = notification
        unread_notification.connect(_signal_listener)

        notification = Notification.objects.get(id=notification.id)
        notification.unread = True
        notification.save()
        self.assertTrue(signal_received)
        self.assertEqual(received_notification, notification)

    def test_unread_notification_signal_on_save_not_trigger(self):
        """
        Test the "unread_notification" signal emission on model save.
        """
        notification = self._get_notification()
        signal_received = False

        def _signal_listener(sender, notification, **kwargs):
            nonlocal signal_received
            signal_received = True
        unread_notification.connect(_signal_listener)

        notification.unread = False
        notification.save()
        self.assertFalse(signal_received)

    def test_notice_unread_notifications_upon_login(self):
        """
        Test of auto notice of unread notification upon login.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='illpassword',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient)
        notification = Notification.objects.create(title='Test 1 (titre)',
                                                   message='Test 1 (msg)',
                                                   message_html='Test 1 (html)',
                                                   recipient=recipient)
        self.assertIsNotNone(notification)

        c = Client()
        response = c.post(reverse('auth:login'), {'username': 'jonhdoe', 'password': 'illpassword'})
        self.assertIsNotNone(response)
        response = c.get('/')
        self.assertIsNotNone(response)
        self.assertEqual(response.context["user"], recipient)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual('unread_notifications', messages[0].extra_tags)

    def test_has_unread_notification_method(self):
        """
        Test the ``has_unread_notification`` method of the manager class.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='illpassword',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient)
        self.assertFalse(Notification.objects.has_unread_notification(recipient))

        notification = Notification.objects.create(title='Test 1 (titre)',
                                                   message='Test 1 (msg)',
                                                   message_html='Test 1 (html)',
                                                   recipient=recipient)
        self.assertIsNotNone(notification)
        self.assertTrue(Notification.objects.has_unread_notification(recipient))

        notification.unread = False
        notification.save()
        self.assertFalse(Notification.objects.has_unread_notification(recipient))

    def test_unread_notifications_count_method(self):
        """
        Test the ``unread_notifications_count`` method of the manager class.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='illpassword',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient)
        self.assertEqual(0, Notification.objects.unread_notifications_count(recipient))

        notification = Notification.objects.create(title='Test 1 (titre)',
                                                   message='Test 1 (msg)',
                                                   message_html='Test 1 (html)',
                                                   recipient=recipient)
        self.assertIsNotNone(notification)
        self.assertEqual(1, Notification.objects.unread_notifications_count(recipient))

        notification.unread = False
        notification.save()
        self.assertEqual(0, Notification.objects.unread_notifications_count(recipient))

    def test_mark_all_notifications_has_read_method(self):
        """
        Test the ``mark_all_notifications_has_read`` method of the manager class.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='illpassword',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient)
        notification = Notification.objects.create(title='Test 1 (titre)',
                                                   message='Test 1 (msg)',
                                                   message_html='Test 1 (html)',
                                                   recipient=recipient)
        self.assertIsNotNone(notification)
        self.assertEqual(1, Notification.objects.unread_notifications_count(recipient))

        Notification.objects.mark_all_notifications_has_read(recipient)
        notification.refresh_from_db()
        self.assertFalse(notification.unread)

    def test_delete_old_notifications_method(self):
        """
        Test the ``delete_old_notifications`` method of the manager class.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='illpassword',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient)
        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            notification = Notification.objects.create(title='Test 1',
                                                       message='Test 1',
                                                       message_html='Test 1',
                                                       recipient=recipient)
            self.assertIsNotNone(notification)

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now - timedelta(days=READ_NOTIFICATION_DELETION_TIMEOUT_DAYS)
            notification = Notification.objects.create(title='Test 2',
                                                       message='Test 2',
                                                       message_html='Test 2',
                                                       recipient=recipient)
            self.assertIsNotNone(notification)
            notification = Notification.objects.create(title='Test 3',
                                                       message='Test 3',
                                                       message_html='Test 3',
                                                       recipient=recipient,
                                                       unread=False)
            self.assertIsNotNone(notification)

        self.assertEqual(3, recipient.notifications.count())
        self.assertEqual(2, Notification.objects.unread_notifications_count(recipient))

        Notification.objects.delete_old_notifications()

        self.assertEqual(1, recipient.notifications.count())
        self.assertEqual(1, Notification.objects.unread_notifications_count(recipient))

    def test_dismiss_notifications_method(self):
        """
        Test the ``dismiss_notifications`` method of the manager class.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='illpassword',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient)
        notification = Notification.objects.create(title='Test 1 (titre)',
                                                   message='Test 1 (msg)',
                                                   message_html='Test 1 (html)',
                                                   recipient=recipient,
                                                   dismiss_code='123456')
        self.assertIsNotNone(notification)
        self.assertTrue(notification.unread)

        Notification.objects.dismiss_notifications(recipient, '123456')
        notification.refresh_from_db()
        self.assertFalse(notification.unread)


class NotificationsUserProfileTestCase(TestCase):
    """
    Tests suite for the ``NotificationsUserProfile`` data model.
    """

    def test_auto_create(self):
        """
        Test the auto creation of user's profile.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='jonhdoe',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient.notifications_profile)
        self.assertIsInstance(recipient.notifications_profile, NotificationsUserProfile)

        # Test defaults
        self.assertTrue(recipient.notifications_profile.send_mail_on_new_notification)
