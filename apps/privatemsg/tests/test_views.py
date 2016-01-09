"""
Tests suite for the views of the private messages app.
"""

from django.test import TestCase, Client
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import (PrivateMessage,
                      BlockedUser)


class NotificationsViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create a new user named "johndoe" with password "illpassword".
        """
        self.user1 = get_user_model().objects.create_user(username='johndoe1',
                                                          password='johndoe1',
                                                          email='john.doe@example.com')
        self.user2 = get_user_model().objects.create_user(username='johndoe2',
                                                          password='johndoe2',
                                                          email='john.doe@example.com')
        self.user3 = get_user_model().objects.create_user(username='johndoe3',
                                                          password='johndoe3',
                                                          email='john.doe@example.com')
        self.msg1 = PrivateMessage.objects.create(sender=self.user1,
                                                  recipient=self.user2,
                                                  subject='Test message 1',
                                                  body='Test message')
        self.msg2 = PrivateMessage.objects.create(sender=self.user1,
                                                  recipient=self.user2,
                                                  read_at=timezone.now(),
                                                  subject='Test message 2',
                                                  body='Test message')
        self.msg3 = PrivateMessage.objects.create(sender=self.user1,
                                                  recipient=self.user2,
                                                  recipient_deleted_at=timezone.now(),
                                                  subject='Test message 3',
                                                  body='Test message')
        self.msg4 = PrivateMessage.objects.create(sender=self.user1,
                                                  recipient=self.user2,
                                                  recipient_permanently_deleted=True,
                                                  subject='Test message 4',
                                                  body='Test message')
        self.msg5 = PrivateMessage.objects.create(sender=self.user2,
                                                  recipient=self.user3,
                                                  subject='Test message 5',
                                                  body='Test message')
        self.block1 = BlockedUser.objects.create(user=self.user1, blocked_user=self.user2)

    def test_private_msg_list_view_available(self):
        """
        Test the availability of the "private messages list" view.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/inbox.html')
        self.assertIn('private_messages', response.context)
        self.assertQuerysetEqual(response.context['private_messages'], ['<PrivateMessage: Test message 2>',
                                                                        '<PrivateMessage: Test message 1>'])

    def test_read_private_msg_list_view_available(self):
        """
        Test the availability of the "read private messages list" view.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:inbox_read'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/inbox.html')
        self.assertIn('private_messages', response.context)
        self.assertQuerysetEqual(response.context['private_messages'], ['<PrivateMessage: Test message 2>'])

    def test_unread_private_msg_list_view_available(self):
        """
        Test the availability of the "unread private messages list" view.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:inbox_unread'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/inbox.html')
        self.assertIn('private_messages', response.context)
        self.assertQuerysetEqual(response.context['private_messages'], ['<PrivateMessage: Test message 1>'])

    def test_private_msg_list_view_redirect_not_login(self):
        """
        Test the redirection of the "private messages list" view when not logged-in.
        """
        client = Client()
        privatemsg_list_url = reverse('privatemsg:inbox')
        response = client.get(privatemsg_list_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, privatemsg_list_url))

    def test_mark_all_private_msg_as_read_view_available(self):
        """
        Test the availability of the "mark all private messages as read" view.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:inbox_mark_all_as_read'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/mark_all_as_read.html')

    def test_mark_all_private_msg_as_read_view_redirect_not_login(self):
        """
        Test the redirection of the "mark all private messages as read" view when not logged-in.
        """
        client = Client()
        mark_all_as_read_url = reverse('privatemsg:inbox_mark_all_as_read')
        response = client.get(mark_all_as_read_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, mark_all_as_read_url))

    def test_outbox_list_view_available(self):
        """
        Test the availability of the "sent private messages list" view.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:outbox'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/outbox.html')
        self.assertIn('private_messages', response.context)
        self.assertQuerysetEqual(response.context['private_messages'], ['<PrivateMessage: Test message 4>',
                                                                        '<PrivateMessage: Test message 3>',
                                                                        '<PrivateMessage: Test message 2>',
                                                                        '<PrivateMessage: Test message 1>'])

    def test_outbox_list_view_redirect_not_login(self):
        """
        Test the redirection of the "sent private messages list" view when not logged-in.
        """
        client = Client()
        outbox_url = reverse('privatemsg:outbox')
        response = client.get(outbox_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, outbox_url))

    def test_trashbox_list_view_available(self):
        """
        Test the availability of the "deleted private messages list" view.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:trash'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/trashbox.html')
        self.assertIn('private_messages', response.context)
        self.assertQuerysetEqual(response.context['private_messages'], ['<PrivateMessage: Test message 3>'])

    def test_trashbox_list_view_redirect_not_login(self):
        """
        Test the redirection of the "deleted private messages list" view when not logged-in.
        """
        client = Client()
        trashbox_url = reverse('privatemsg:trash')
        response = client.get(trashbox_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, trashbox_url))

    def test_delete_all_deleted_msg_permanently_view_available(self):
        """
        Test the availability of the "empty trash" view.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:delete_all_deleted_msg_permanently'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/trashbox_cleanup.html')

    def test_delete_all_deleted_msg_permanently_view_redirect_not_login(self):
        """
        Test the redirection of the "empty trash" view when not logged-in.
        """
        client = Client()
        delete_all_deleted_msg_url = reverse('privatemsg:delete_all_deleted_msg_permanently')
        response = client.get(delete_all_deleted_msg_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, delete_all_deleted_msg_url))

    def test_msg_compose_view_available(self):
        """
        Test the availability of the "compose message" view.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:compose'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_compose.html')

    def test_msg_compose_to_view_available(self):
        """
        Test the availability of the "compose to message" view.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:compose_to', kwargs={'recipient': 'johndoe2'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_compose.html')

    def test_msg_compose_view_redirect_not_login(self):
        """
        Test the redirection of the "compose message" view when not logged-in.
        """
        client = Client()
        compose_msg_url = reverse('privatemsg:compose')
        response = client.get(compose_msg_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, compose_msg_url))

    def test_msg_detail_view_available_as_sender(self):
        """
        Test the availability of the "message detail" view as sender.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_detail', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_detail.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)
        self.assertIn('is_sender', response.context)
        self.assertTrue(response.context['is_sender'])
        self.assertIn('is_recipient', response.context)
        self.assertFalse(response.context['is_recipient'])

    def test_msg_detail_view_available_as_recipient(self):
        """
        Test the availability of the "message detail" view as recipient.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:msg_detail', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_detail.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)
        self.assertIn('is_recipient', response.context)
        self.assertTrue(response.context['is_recipient'])
        self.assertIn('is_sender', response.context)
        self.assertFalse(response.context['is_sender'])

    def test_msg_detail_view_not_available_as_thirdparty(self):
        """
        Test the UN-availability of the "message detail" view as a third party.
        """
        client = Client()
        client.login(username='johndoe3', password='johndoe3')
        response = client.get(reverse('privatemsg:msg_detail', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_detail_view_with_unknown_msg(self):
        """
        Test the UN-availability of the "message detail" view with an unknown message PK.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_detail', kwargs={'pk': '1337'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_detail_view_redirect_not_login(self):
        """
        Test the redirection of the "message detail" view when not logged-in.
        """
        client = Client()
        msg_details_url = reverse('privatemsg:msg_detail', kwargs={'pk': self.msg1.pk})
        response = client.get(msg_details_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_details_url))

    def test_msg_reply_view_available_as_sender(self):
        """
        Test the availability of the "message reply" view as sender.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_reply', kwargs={'parent_pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_reply.html')
        self.assertIn('parent_msg', response.context)
        self.assertEqual(response.context['parent_msg'], self.msg1)

    def test_msg_reply_view_available_as_recipient(self):
        """
        Test the availability of the "message reply" view as sender.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:msg_reply', kwargs={'parent_pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_reply.html')
        self.assertIn('parent_msg', response.context)
        self.assertEqual(response.context['parent_msg'], self.msg1)

    def test_msg_reply_view_not_available_as_thirdparty(self):
        """
        Test the UN-availability of the "message reply" view as a third party.
        """
        client = Client()
        client.login(username='johndoe3', password='johndoe3')
        response = client.get(reverse('privatemsg:msg_reply', kwargs={'parent_pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_reply_view_with_unknown_msg(self):
        """
        Test the UN-availability of the "message reply" view with an unknown message PK.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_reply', kwargs={'parent_pk': '1337'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_reply_view_redirect_not_login(self):
        """
        Test the redirection of the "message reply" view when not logged-in.
        """
        client = Client()
        msg_reply_url = reverse('privatemsg:msg_reply', kwargs={'parent_pk': self.msg1.pk})
        response = client.get(msg_reply_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_reply_url))

    def test_my_account_view_redirect_not_login(self):
        """
        Test the redirection of the "my account" view when not logged-in.
        """
        client = Client()
        myaccount_url = reverse('privatemsg:myaccount')
        response = client.get(myaccount_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, myaccount_url))

    def test_my_account_view_available(self):
        """
        Test the availability of the "my account" view when logged-in.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:myaccount'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/my_account.html')

    def test_msg_delete_view_available_as_sender(self):
        """
        Test the availability of the "delete message" view as sender.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_delete', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_delete_confirm.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)

    def test_msg_delete_view_available_as_recipient(self):
        """
        Test the availability of the "delete message" view as sender.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:msg_delete', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_delete_confirm.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)

    def test_msg_delete_view_not_available_as_thirdparty(self):
        """
        Test the UN-availability of the "delete message" view as a third party.
        """
        client = Client()
        client.login(username='johndoe3', password='johndoe3')
        response = client.get(reverse('privatemsg:msg_delete', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_delete_view_with_unknown_msg(self):
        """
        Test the UN-availability of the "delete message" view with an unknown message PK.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_delete', kwargs={'pk': '1337'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_delete_view_redirect_not_login(self):
        """
        Test the redirection of the "delete message" view when not logged-in.
        """
        client = Client()
        msg_delete_url = reverse('privatemsg:msg_delete', kwargs={'pk': self.msg1.pk})
        response = client.get(msg_delete_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_delete_url))

    def test_msg_delete_permanent_view_available_as_sender(self):
        """
        Test the availability of the "permanently delete message" view as sender.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_delete_permanent', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_delete_permanent_confirm.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)

    def test_msg_delete_permanent_view_available_as_recipient(self):
        """
        Test the availability of the "permanently delete message" view as sender.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:msg_delete_permanent', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_delete_permanent_confirm.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)

    def test_msg_delete_permanent_view_not_available_as_thirdparty(self):
        """
        Test the UN-availability of the "permanently delete message" view as a third party.
        """
        client = Client()
        client.login(username='johndoe3', password='johndoe3')
        response = client.get(reverse('privatemsg:msg_delete_permanent', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_delete_permanent_view_with_unknown_msg(self):
        """
        Test the UN-availability of the "permanently delete message" view with an unknown message PK.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_delete_permanent', kwargs={'pk': '1337'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_delete_permanent_view_redirect_not_login(self):
        """
        Test the redirection of the "permanently delete message" view when not logged-in.
        """
        client = Client()
        msg_reply_url = reverse('privatemsg:msg_delete_permanent', kwargs={'pk': self.msg1.pk})
        response = client.get(msg_reply_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_reply_url))

    def test_msg_undelete_view_available_as_sender(self):
        """
        Test the availability of the "undelete message" view as sender.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_undelete', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_undelete_confirm.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)

    def test_msg_undelete_view_available_as_recipient(self):
        """
        Test the availability of the "undelete message" view as sender.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:msg_undelete', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/msg_undelete_confirm.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], self.msg1)

    def test_msg_undelete_view_not_available_as_thirdparty(self):
        """
        Test the UN-availability of the "undelete message" view as a third party.
        """
        client = Client()
        client.login(username='johndoe3', password='johndoe3')
        response = client.get(reverse('privatemsg:msg_undelete', kwargs={'pk': self.msg1.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_undelete_view_with_unknown_msg(self):
        """
        Test the UN-availability of the "undelete message" view with an unknown message PK.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:msg_undelete', kwargs={'pk': '1337'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_undelete_view_with_permanently_deleted_msg(self):
        """
        Test the UN-availability of the "undelete message" view with an already permanently deleted message PK.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:msg_undelete', kwargs={'pk':  self.msg4.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_msg_undelete_view_redirect_not_login(self):
        """
        Test the redirection of the "undelete message" view when not logged-in.
        """
        client = Client()
        msg_undelete_url = reverse('privatemsg:msg_undelete', kwargs={'pk': self.msg1.pk})
        response = client.get(msg_undelete_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_undelete_url))

    def test_blocked_user_list_view_available(self):
        """
        Test the availability of the "blocked user list" view.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:blocked_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/blocked_user_list.html')
        self.assertIn('blocked_users', response.context)
        self.assertQuerysetEqual(response.context['blocked_users'],
                                 ['<BlockedUser: User "johndoe1" blocking "johndoe2">'])

    def test_blocked_user_list_view_redirect_not_login(self):
        """
        Test the redirection of the "undelete message" view when not logged-in.
        """
        client = Client()
        msg_undelete_url = reverse('privatemsg:blocked_users')
        response = client.get(msg_undelete_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_undelete_url))

    def test_block_user_view_available(self):
        """
        Test the availability of the "block user" view.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:block_user', kwargs={'username': self.user2}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/block_user.html')
        self.assertIn('blocked_user', response.context)
        self.assertEqual(response.context['blocked_user'], self.user2)
        self.assertIn('trying_self_block', response.context)
        self.assertFalse(response.context['trying_self_block'])

    def test_block_user_view_available_self_block(self):
        """
        Test the availability of the "block user" view when trying to block himself.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:block_user', kwargs={'username': self.user1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/block_user.html')
        self.assertIn('blocked_user', response.context)
        self.assertEqual(response.context['blocked_user'], self.user1)
        self.assertIn('trying_self_block', response.context)
        self.assertTrue(response.context['trying_self_block'])

    def test_block_user_view_available_staff_block(self):
        """
        Test the availability of the "block user" view when trying to block an admin.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        self.user3.is_staff = True
        self.user3.save()
        response = client.get(reverse('privatemsg:block_user', kwargs={'username': self.user3}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/block_user.html')
        self.assertIn('blocked_user', response.context)
        self.assertEqual(response.context['blocked_user'], self.user3)
        self.assertIn('trying_block_staff', response.context)
        self.assertTrue(response.context['trying_block_staff'])

    def test_block_user_view_with_unknown_nickname(self):
        """
        Test the UN-availability of the "block user" view with an unknown user name.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:block_user', kwargs={'username': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_block_user_view_redirect_not_login(self):
        """
        Test the redirection of the "undelete message" view when not logged-in.
        """
        client = Client()
        msg_undelete_url = reverse('privatemsg:block_user', kwargs={'username': self.user1})
        response = client.get(msg_undelete_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_undelete_url))

    def test_unblock_user_view_available(self):
        """
        Test the availability of the "unblock user" view.
        """
        client = Client()
        client.login(username='johndoe1', password='johndoe1')
        response = client.get(reverse('privatemsg:unblock_user', kwargs={'username': self.user2}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privatemsg/unblock_user.html')
        self.assertIn('blocked_user', response.context)
        self.assertEqual(response.context['blocked_user'], self.user2)

    def test_unblock_user_view_with_unknown_nickname(self):
        """
        Test the UN-availability of the "block user" view with an unknown user name.
        """
        client = Client()
        client.login(username='johndoe2', password='johndoe2')
        response = client.get(reverse('privatemsg:unblock_user', kwargs={'username': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_unblock_user_view_redirect_not_login(self):
        """
        Test the redirection of the "undelete message" view when not logged-in.
        """
        client = Client()
        msg_undelete_url = reverse('privatemsg:unblock_user', kwargs={'username': self.user1})
        response = client.get(msg_undelete_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, msg_undelete_url))
