"""
Tests suite for the models of the private messages app.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, Client
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from ..models import (PrivateMessage,
                      BlockedUser,
                      PrivateMessageUserProfile)
from ..settings import (NB_SECONDS_BETWEEN_PRIVATE_MSG,
                        DELETED_MSG_DELETION_TIMEOUT_DAYS,
                        DELETED_MSG_PHYSICAL_DELETION_TIMEOUT_DAYS)


class PrivateMessageTestCase(TestCase):
    """
    Tests suite for the ``PrivateMessage`` data model.
    """

    def setUp(self):
        """
        Create some test fixtures.
        """
        self.sender = get_user_model().objects.create_user(username='jonhdoe',
                                                           password='jonhdoe',
                                                           email='jonh.doe@example.com')
        self.recipient = get_user_model().objects.create_user(username='jonhsmith',
                                                              password='jonhsmith',
                                                              email='jonh.smith@example.com')
        self.msg = PrivateMessage.objects.create(sender=self.sender,
                                                 recipient=self.recipient,
                                                 subject='Test message',
                                                 body='Test message')

    def test_default_values(self):
        """
        Test default values of the newly created message.
        """
        self.assertIsNone(self.msg.parent_msg)
        self.assertIsNotNone(self.msg.sent_at)
        self.assertIsNone(self.msg.read_at)
        self.assertIsNone(self.msg.sender_deleted_at)
        self.assertIsNone(self.msg.recipient_deleted_at)
        self.assertFalse(self.msg.sender_permanently_deleted)
        self.assertFalse(self.msg.recipient_permanently_deleted)

    def test_str_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        self.assertEqual(self.msg.subject, str(self.msg))

    def test_str_method_no_subject(self):
        """
        Test ``__str__`` result for other tests.
        """
        self.msg.subject = ''
        self.assertEqual(_('(no subject)'), str(self.msg))

    def test_fix_deletion_error_state(self):
        """
        Test if the save method handle erroneous states.
        """
        self.msg.recipient_permanently_deleted = True
        self.msg.recipient_deleted_at = None
        self.msg.fix_deletion_states()
        self.assertTrue(self.msg.recipient_permanently_deleted)
        self.assertIsNotNone(self.msg.recipient_deleted_at)

        self.msg.sender_permanently_deleted = True
        self.msg.sender_deleted_at = None
        self.msg.fix_deletion_states()
        self.assertTrue(self.msg.sender_permanently_deleted)
        self.assertIsNotNone(self.msg.sender_deleted_at)

    def test_get_absolute_url_method(self):
        """
        Test ``get_absolute_url`` method with a valid message.
        """
        excepted_url = reverse('privatemsg:msg_detail', kwargs={'pk': self.msg.pk})
        self.assertEqual(excepted_url, self.msg.get_absolute_url())

    def test_get_reply_url_method(self):
        """
        Test ``get_reply_url`` method with a valid message.
        """
        excepted_url = reverse('privatemsg:msg_reply', kwargs={'parent_pk': self.msg.pk})
        self.assertEqual(excepted_url, self.msg.get_reply_url())

    def test_get_delete_url_method(self):
        """
        Test ``get_delete_url`` method with a valid message.
        """
        excepted_url = reverse('privatemsg:msg_delete', kwargs={'pk': self.msg.pk})
        self.assertEqual(excepted_url, self.msg.get_delete_url())

    def test_get_delete_permanent_url_method(self):
        """
        Test ``get_delete_permanent_url`` method with a valid message.
        """
        excepted_url = reverse('privatemsg:msg_delete_permanent', kwargs={'pk': self.msg.pk})
        self.assertEqual(excepted_url, self.msg.get_delete_permanent_url())

    def test_get_undelete_url_method(self):
        """
        Test ``get_undelete_url`` method with a valid message.
        """
        excepted_url = reverse('privatemsg:msg_undelete', kwargs={'pk': self.msg.pk})
        self.assertEqual(excepted_url, self.msg.get_undelete_url())

    def test_get_subject_display_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        self.assertEqual(self.msg.subject, self.msg.get_subject_display())

    def test_get_subject_display_method_no_subject(self):
        """
        Test ``__str__`` result for other tests.
        """
        self.msg.subject = ''
        self.assertEqual(_('(no subject)'), self.msg.get_subject_display())

    def test_unread(self):
        """
        Test the ``urnead`` method of the model.
        """
        self.msg.read_at = None
        self.assertTrue(self.msg.unread())

        self.msg.read_at = timezone.now()
        self.assertFalse(self.msg.unread())

    def test_deleted_at_recipient_side(self):
        """
        Test the ``deleted_at_recipient_side`` of the model.
        """
        self.msg.recipient_deleted_at = None
        self.msg.recipient_permanently_deleted = False
        self.assertFalse(self.msg.deleted_at_recipient_side())

        self.msg.recipient_deleted_at = timezone.now()
        self.msg.recipient_permanently_deleted = False
        self.assertTrue(self.msg.deleted_at_recipient_side())

        self.msg.recipient_deleted_at = None
        self.msg.recipient_permanently_deleted = True
        self.assertTrue(self.msg.deleted_at_recipient_side())

        self.msg.recipient_deleted_at = timezone.now()
        self.msg.recipient_permanently_deleted = True
        self.assertTrue(self.msg.deleted_at_recipient_side())

    def test_deleted_at_sender_side(self):
        """
        Test the ``deleted_at_sender_side`` of the model.
        """
        self.msg.sender_deleted_at = None
        self.msg.sender_permanently_deleted = False
        self.assertFalse(self.msg.deleted_at_sender_side())

        self.msg.sender_deleted_at = timezone.now()
        self.msg.sender_permanently_deleted = False
        self.assertTrue(self.msg.deleted_at_sender_side())

        self.msg.sender_deleted_at = None
        self.msg.sender_permanently_deleted = True
        self.assertTrue(self.msg.deleted_at_sender_side())

        self.msg.sender_deleted_at = timezone.now()
        self.msg.sender_permanently_deleted = True
        self.assertTrue(self.msg.deleted_at_sender_side())

    def test_is_recipient(self):
        """
        Test the ``is_recipient`` of the model.
        """
        self.assertFalse(self.msg.is_recipient(self.sender))
        self.assertTrue(self.msg.is_recipient(self.recipient))

    def test_is_sender(self):
        """
        Test the ``is_sender`` of the model.
        """
        self.assertFalse(self.msg.is_sender(self.recipient))
        self.assertTrue(self.msg.is_sender(self.sender))

    def test_permanently_deleted_from_user_side(self):
        """
        Test the ``permanently_deleted_from_user_side`` method of the model.
        """
        self.msg.sender_permanently_deleted = False
        self.msg.recipient_permanently_deleted = False
        self.assertFalse(self.msg.permanently_deleted_from_user_side(self.sender))
        self.assertFalse(self.msg.permanently_deleted_from_user_side(self.recipient))

        self.msg.sender_permanently_deleted = True
        self.msg.recipient_permanently_deleted = False
        self.assertTrue(self.msg.permanently_deleted_from_user_side(self.sender))
        self.assertFalse(self.msg.permanently_deleted_from_user_side(self.recipient))

        self.msg.sender_permanently_deleted = False
        self.msg.recipient_permanently_deleted = True
        self.assertFalse(self.msg.permanently_deleted_from_user_side(self.sender))
        self.assertTrue(self.msg.permanently_deleted_from_user_side(self.recipient))

        self.msg.sender_permanently_deleted = True
        self.msg.recipient_permanently_deleted = True
        self.assertTrue(self.msg.permanently_deleted_from_user_side(self.sender))
        self.assertTrue(self.msg.permanently_deleted_from_user_side(self.recipient))

    def test_delete_from_user_side_sender(self):
        """
        Test the ``delete_from_user_side`` method of the model as sender.
        """
        self.assertIsNone(self.msg.sender_deleted_at)
        self.assertFalse(self.msg.sender_permanently_deleted)
        self.msg.delete_from_user_side(self.sender)
        self.assertIsNotNone(self.msg.sender_deleted_at)
        self.assertFalse(self.msg.sender_permanently_deleted)

    def test_delete_from_user_side_sender_permanent(self):
        """
        Test the ``delete_from_user_side`` method of the model as sender with permanent flag set.
        """
        self.assertIsNone(self.msg.sender_deleted_at)
        self.assertFalse(self.msg.sender_permanently_deleted)
        self.msg.delete_from_user_side(self.sender, permanent=True)
        self.assertIsNotNone(self.msg.sender_deleted_at)
        self.assertTrue(self.msg.sender_permanently_deleted)

    def test_delete_from_user_side_recipient(self):
        """
        Test the ``delete_from_user_side`` method of the model as recipient.
        """
        self.assertIsNone(self.msg.recipient_deleted_at)
        self.assertFalse(self.msg.recipient_permanently_deleted)
        self.msg.delete_from_user_side(self.recipient)
        self.assertIsNotNone(self.msg.recipient_deleted_at)
        self.assertFalse(self.msg.recipient_permanently_deleted)

    def test_delete_from_user_side_recipient_permanent(self):
        """
        Test the ``delete_from_user_side`` method of the model as recipient with permanent flag set.
        """
        self.assertIsNone(self.msg.recipient_deleted_at)
        self.assertFalse(self.msg.recipient_permanently_deleted)
        self.msg.delete_from_user_side(self.recipient, permanent=True)
        self.assertIsNotNone(self.msg.recipient_deleted_at)
        self.assertTrue(self.msg.recipient_permanently_deleted)

    def test_undelete_from_user_side_sender(self):
        """
        Test the ``undelete_from_user_side`` method of the model as sender.
        """
        self.msg.sender_deleted_at = timezone.now()
        self.msg.sender_permanently_deleted = True
        self.msg.undelete_from_user_side(self.sender)
        self.assertIsNone(self.msg.sender_deleted_at)
        self.assertFalse(self.msg.sender_permanently_deleted)

    def test_undelete_from_user_side_recipient(self):
        """
        Test the ``undelete_from_user_side`` method of the model as recipient.
        """
        self.msg.recipient_deleted_at = timezone.now()
        self.msg.recipient_permanently_deleted = True
        self.msg.undelete_from_user_side(self.recipient)
        self.assertIsNone(self.msg.recipient_deleted_at)
        self.assertFalse(self.msg.recipient_permanently_deleted)

    def test_notice_unread_messages_upon_login(self):
        """
        Test of unread message notice generation upon login.
        """
        c = Client()
        response = c.post(reverse('auth:login'), {'username': 'jonhsmith', 'password': 'jonhsmith'})
        self.assertIsNotNone(response)
        response = c.get('/')
        self.assertIsNotNone(response)
        self.assertEqual(response.context["user"], self.recipient)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual('unread_pvmessages', messages[0].extra_tags)

    def test_inbox_count_for_method(self):
        """
        Test the ``inbox_count_for`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_permanently_deleted=True,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)

        inbox_count = PrivateMessage.objects.inbox_count_for(user2)
        self.assertEqual(1, inbox_count)

    def test_inbox_for_method(self):
        """
        Test the ``inbox_for`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_permanently_deleted=True,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)

        inbox = PrivateMessage.objects.inbox_for(user2)
        self.assertEqual(list(inbox), [msg2, msg1])

    def test_mark_all_messages_has_read_method(self):
        """
        Test the ``mark_all_messages_has_read_for`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        old_now = timezone.now()
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=old_now,
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_permanently_deleted=True,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)
        self.assertIsNone(msg1.read_at)
        self.assertEqual(old_now, msg2.read_at)
        self.assertIsNone(msg3.read_at)
        self.assertIsNone(msg4.read_at)

        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            PrivateMessage.objects.mark_all_messages_has_read_for(user2)

        msg1.refresh_from_db()
        msg2.refresh_from_db()
        msg3.refresh_from_db()
        msg4.refresh_from_db()

        self.assertEqual(now, msg1.read_at)
        self.assertEqual(old_now, msg2.read_at)
        self.assertIsNone(msg3.read_at)
        self.assertIsNone(msg4.read_at)

    def test_outbox_for_method(self):
        """
        Test the ``outbox_for`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        msg1 = PrivateMessage.objects.create(sender=user3,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_permanently_deleted=True,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)

        outbox = PrivateMessage.objects.outbox_for(user1)
        self.assertEqual(list(outbox), [msg5, msg4, msg3, msg2])

    def test_trash_for_method(self):
        """
        Test the ``trash_for`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        at_deletion_threshold = timezone.now() - timedelta(days=DELETED_MSG_DELETION_TIMEOUT_DAYS)
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=at_deletion_threshold,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_permanently_deleted=True,
                                             subject='Test message',
                                             body='Test message')
        msg6 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)
        self.assertIsNotNone(msg6)

        trashbox = PrivateMessage.objects.trash_for(user2)
        self.assertEqual(list(trashbox), [msg3])

    def test_trash_for_method_2(self):
        """
        Test the ``trash_for`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             sender_deleted_at=timezone.now(),
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        at_deletion_threshold = timezone.now() - timedelta(days=DELETED_MSG_DELETION_TIMEOUT_DAYS)
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             sender_deleted_at=at_deletion_threshold,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             sender_permanently_deleted=True,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg6 = PrivateMessage.objects.create(sender=user2,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)
        self.assertIsNotNone(msg6)

        trashbox = PrivateMessage.objects.trash_for(user1)
        self.assertEqual(list(trashbox), [msg3])

    def test_empty_trash_of_method(self):
        """
        Test the ``empty_trash_of`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        at_deletion_threshold = timezone.now() - timedelta(days=DELETED_MSG_DELETION_TIMEOUT_DAYS)
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=at_deletion_threshold,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_permanently_deleted=True,
                                             subject='Test message',
                                             body='Test message')
        msg6 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)
        self.assertIsNotNone(msg6)

        self.assertFalse(msg3.recipient_permanently_deleted)
        PrivateMessage.objects.empty_trash_of(user2)
        msg3.refresh_from_db()
        self.assertTrue(msg3.recipient_permanently_deleted)

        trashbox = PrivateMessage.objects.trash_for(user2)
        self.assertEqual(list(trashbox), [])

    def test_empty_trash_of_method_2(self):
        """
        Test the ``empty_trash_of`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             read_at=timezone.now(),
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             sender_deleted_at=timezone.now(),
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        at_deletion_threshold = timezone.now() - timedelta(days=DELETED_MSG_DELETION_TIMEOUT_DAYS)
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             sender_deleted_at=at_deletion_threshold,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             sender_permanently_deleted=True,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg6 = PrivateMessage.objects.create(sender=user2,
                                             recipient=user3,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)
        self.assertIsNotNone(msg6)

        self.assertFalse(msg3.sender_permanently_deleted)
        PrivateMessage.objects.empty_trash_of(user1)
        msg3.refresh_from_db()
        self.assertTrue(msg3.sender_permanently_deleted)

        trashbox = PrivateMessage.objects.trash_for(user1)
        self.assertEqual(list(trashbox), [])

    def test_delete_deleted_msg_method(self):
        """
        Test the ``delete_deleted_msg`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        now = timezone.now()
        logical_deletion_date = now - timedelta(days=DELETED_MSG_DELETION_TIMEOUT_DAYS)
        physical_deletion_date = now - timedelta(days=DELETED_MSG_PHYSICAL_DELETION_TIMEOUT_DAYS)
        msg1 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg2 = PrivateMessage.objects.create(sender=user1,
                                             recipient=user2,
                                             recipient_deleted_at=physical_deletion_date,
                                             subject='Test message',
                                             body='Test message')
        msg3 = PrivateMessage.objects.create(sender=user1,
                                             sender_deleted_at=physical_deletion_date,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg4 = PrivateMessage.objects.create(sender=user1,
                                             sender_deleted_at=physical_deletion_date,
                                             recipient=user2,
                                             recipient_deleted_at=physical_deletion_date,
                                             subject='Test message',
                                             body='Test message')
        msg5 = PrivateMessage.objects.create(sender=user1,
                                             sender_deleted_at=logical_deletion_date,
                                             recipient=user2,
                                             subject='Test message',
                                             body='Test message')
        msg6 = PrivateMessage.objects.create(sender=user2,
                                             recipient=user3,
                                             recipient_deleted_at=logical_deletion_date,
                                             subject='Test message',
                                             body='Test message')
        self.assertIsNotNone(msg1)
        self.assertIsNotNone(msg2)
        self.assertIsNotNone(msg3)
        self.assertIsNotNone(msg4)
        self.assertIsNotNone(msg5)
        self.assertIsNotNone(msg6)

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            PrivateMessage.objects.delete_deleted_msg()

        messages = PrivateMessage.objects.all()
        self.assertEqual(list(messages), [msg6, msg5, msg3, msg2, msg1, self.msg])

        msg5.refresh_from_db()
        msg6.refresh_from_db()
        self.assertTrue(msg5.sender_permanently_deleted)
        self.assertFalse(msg5.recipient_permanently_deleted)
        self.assertFalse(msg6.sender_permanently_deleted)
        self.assertTrue(msg6.recipient_permanently_deleted)


class BlockedUserTestCase(TestCase):
    """
    Tests suite for the ``BlockedUser`` data model.
    """

    def test_init(self):
        """
        Test the ``last_block_date`` auto init.
        """
        user = get_user_model().objects.create_user(username='jonhdoe',
                                                    password='jonhdoe',
                                                    email='jonh.doe@example.com')
        buser = BlockedUser.objects.create(user=user, blocked_user=user)
        self.assertIsNotNone(buser.last_block_date)
        self.assertTrue(buser.active)

    def test_str_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        user = get_user_model().objects.create_user(username='jonhdoe',
                                                    password='jonhdoe',
                                                    email='jonh.doe@example.com')
        buser = BlockedUser.objects.create(user=user, blocked_user=user)
        self.assertEqual('User "%s" blocking "%s"' % (buser.user.username,
                                                      buser.blocked_user.username), str(buser))

    def test_blocked_users_for_method(self):
        """
        Test the ``blocked_users_for`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        b1 = BlockedUser.objects.create(user=user1, blocked_user=user2)
        BlockedUser.objects.create(user=user3, blocked_user=user2)
        self.assertEqual(list(BlockedUser.objects.blocked_users_for(user1)), [b1])

    def test_has_blocked_user_method(self):
        """
        Test the ``has_blocked_user`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        BlockedUser.objects.create(user=user1, blocked_user=user2)
        BlockedUser.objects.create(user=user3, blocked_user=user2)
        self.assertTrue(BlockedUser.objects.has_blocked_user(user1, user2))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user1, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user1))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user3, user1))
        self.assertTrue(BlockedUser.objects.has_blocked_user(user3, user2))

    def test_block_user_method(self):
        """
        Test the ``block_user`` method of the manager class.
        """

        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        self.assertFalse(BlockedUser.objects.has_blocked_user(user1, user2))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user1, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user1))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user3, user1))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user3, user2))

        BlockedUser.objects.block_user(user1, user2)

        self.assertTrue(BlockedUser.objects.has_blocked_user(user1, user2))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user1, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user1))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user3, user1))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user3, user2))

    def test_unblock_user_method(self):
        """
        Test the ``unblock_user`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='jonhdoe1',
                                                     password='jonhdoe1',
                                                     email='jonh.doe@example.com')
        user2 = get_user_model().objects.create_user(username='jonhdoe2',
                                                     password='jonhdoe2',
                                                     email='jonh.doe@example.com')
        user3 = get_user_model().objects.create_user(username='jonhdoe3',
                                                     password='jonhdoe3',
                                                     email='jonh.doe@example.com')
        BlockedUser.objects.create(user=user1, blocked_user=user2)
        BlockedUser.objects.create(user=user3, blocked_user=user2)
        self.assertTrue(BlockedUser.objects.has_blocked_user(user1, user2))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user1, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user1))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user3, user1))
        self.assertTrue(BlockedUser.objects.has_blocked_user(user3, user2))

        BlockedUser.objects.unblock_user(user1, user2)

        self.assertFalse(BlockedUser.objects.has_blocked_user(user1, user2))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user1, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user1))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user2, user3))
        self.assertFalse(BlockedUser.objects.has_blocked_user(user3, user1))
        self.assertTrue(BlockedUser.objects.has_blocked_user(user3, user2))


class PrivateMessageUserProfileTestCase(TestCase):
    """
    Tests suite for the ``PrivateMessageUserProfile`` data model.
    """

    def test_auto_create(self):
        """
        Test the auto creation of user's profile.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='jonhdoe',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient.privatemsg_profile)
        self.assertIsInstance(recipient.privatemsg_profile, PrivateMessageUserProfile)

        # Test defaults
        self.assertTrue(recipient.privatemsg_profile.notify_on_new_privmsg)
        self.assertTrue(recipient.privatemsg_profile.accept_privmsg)
        self.assertIsNone(recipient.privatemsg_profile.last_sent_private_msg_date)

    def test_anti_flood_no_last_sent_private_msg_date(self):
        """
        Test the anti-flood system when the ``last_sent_private_msg_date`` is none.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='jonhdoe',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient.privatemsg_profile)
        self.assertIsNone(recipient.privatemsg_profile.last_sent_private_msg_date)
        self.assertFalse(recipient.privatemsg_profile.is_flooding())

    def test_anti_flood_no_trigger(self):
        """
        Test the anti-flood system when the ``last_sent_private_msg_date`` is after the anti-flood time window.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='jonhdoe',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient.privatemsg_profile)
        recipient.privatemsg_profile.last_sent_private_msg_date = timezone.now() - timedelta(seconds=NB_SECONDS_BETWEEN_PRIVATE_MSG)
        self.assertFalse(recipient.privatemsg_profile.is_flooding())

    def test_anti_flood_trigger(self):
        """
        Test the anti-flood system when the ``last_sent_private_msg_date`` is after the anti-flood time window.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='jonhdoe',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient.privatemsg_profile)
        recipient.privatemsg_profile.last_sent_private_msg_date = timezone.now() - timedelta(seconds=NB_SECONDS_BETWEEN_PRIVATE_MSG - 1)
        self.assertTrue(recipient.privatemsg_profile.is_flooding())

    def test_rearm_flooding_delay_and_save(self):
        """
        Test the ``rearm_flooding_delay_and_save`` method of the model.
        """
        recipient = get_user_model().objects.create_user(username='jonhdoe',
                                                         password='jonhdoe',
                                                         email='jonh.doe@example.com')
        self.assertIsNotNone(recipient.privatemsg_profile)
        self.assertIsNone(recipient.privatemsg_profile.last_sent_private_msg_date)
        recipient.privatemsg_profile.rearm_flooding_delay_and_save()
        recipient.privatemsg_profile.refresh_from_db()
        self.assertIsNotNone(recipient.privatemsg_profile.last_sent_private_msg_date)
