"""
Tests suite for the forms of the private messages app.
"""

from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model

from ..forms import (_re_subject,
                     PrivateMessageCreationForm,
                     PrivateMessageReplyForm)
from ..models import (PrivateMessage,
                      BlockedUser)


class MsgSubjectTestCase(SimpleTestCase):
    """
    Tests case for the ``_re_subject`` utility.
    """

    def test_no_subject(self):
        """
        Test the ``_re_subject`` function with no subject line.
        """
        self.assertEqual('Re:', _re_subject(''))

    def test_simple_subject(self):
        """
        Test the ``_re_subject`` function with a simple subject line starting with "Re:".
        """
        self.assertEqual('Re: Test', _re_subject('Re: Test'))

    def test_non_re_subject(self):
        """
        Test the ``_re_subject`` function with a subject line without a "Re:" but less than 200 char long.
        """
        self.assertEqual('Re: Test', _re_subject('Test'))

    def test_long_non_re_subject(self):
        """
        Test the ``_re_subject`` function with a subject line without a "Re:" and more than 200 char long.
        """
        self.assertEqual('Re: ' + 'A' * 250, _re_subject('A' * 300))


class PrivateMessageCreationFormTestCase(TestCase):
    """
    Tests case for the ``PrivateMessageCreationForm`` form.
    """

    def _get_test_users(self):
        """
        Return some test users.
        """
        sender = get_user_model().objects.create_user(username='sender',
                                                      password='illpassword',
                                                      email='sender@example.com')
        recipient = get_user_model().objects.create_user(username='recipient',
                                                         password='illpassword',
                                                         email='recipient@example.com')
        return sender, recipient

    def test_init(self):
        """
        Test if the form can be instantiate.
        """
        user = get_user_model().objects.create_user(username='dummy',
                                                    password='illpassword',
                                                    email='dummy@example.com')
        form = PrivateMessageCreationForm(sender=user)
        self.assertEqual(user, form.sender)

    def test_multiple_recipient(self):
        """
        Test if the form raise a validation error if multiple recipient are set.
        """
        sender, recipient = self._get_test_users()
        post = {
            'subject': 'test',
            'body': 'Test',
            'recipient': 'sender, recipient',
        }
        form = PrivateMessageCreationForm(post, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('recipient', errors)
        self.assertEqual(len(errors['recipient']), 1)
        self.assertEqual(errors['recipient'][0].code, 'multiple_recipients')

    def test_multiple_recipient2(self):
        """
        Test if the form raise a validation error if multiple recipient are set (semi colon variant).
        """
        sender, recipient = self._get_test_users()
        post = {
            'subject': 'test',
            'body': 'Test',
            'recipient': 'sender; recipient',
        }
        form = PrivateMessageCreationForm(post, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('recipient', errors)
        self.assertEqual(len(errors['recipient']), 1)
        self.assertEqual(errors['recipient'][0].code, 'multiple_recipients')

    def test_unknown_recipient(self):
        """
        Test if the form raise a validation error if an unknown recipient is set.
        """
        sender, recipient = self._get_test_users()
        post = {
            'subject': 'test',
            'body': 'Test',
            'recipient': 'unknown',
        }
        form = PrivateMessageCreationForm(post, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('recipient', errors)
        self.assertEqual(len(errors['recipient']), 1)
        self.assertEqual(errors['recipient'][0].code, 'unknown_recipient')

    def test_inactive_recipient(self):
        """
        Test if the form raise a validation error if an inactive recipient is set.
        """
        sender, recipient = self._get_test_users()
        recipient.is_active = False
        recipient.save()
        post = {
            'subject': 'test',
            'body': 'Test',
            'recipient': 'recipient',
        }
        form = PrivateMessageCreationForm(post, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('recipient', errors)
        self.assertEqual(len(errors['recipient']), 1)
        self.assertEqual(errors['recipient'][0].code, 'recipient_account_closed')

    def test_do_not_disturb_recipient(self):
        """
        Test if the form raise a validation error if a recipient who do not accept private message is set.
        """
        sender, recipient = self._get_test_users()
        recipient.privatemsg_profile.accept_privmsg = False
        recipient.privatemsg_profile.save()
        post = {
            'subject': 'test',
            'body': 'Test',
            'recipient': 'recipient',
        }
        form = PrivateMessageCreationForm(post, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('recipient', errors)
        self.assertEqual(len(errors['recipient']), 1)
        self.assertEqual(errors['recipient'][0].code, 'recipient_refuse_privatemsg')

    def test_blocked_by_recipient(self):
        """
        Test if the form raise a validation error if the recipient has block the sender is set.
        """
        sender, recipient = self._get_test_users()
        BlockedUser.objects.create(user=recipient, blocked_user=sender)
        post = {
            'subject': 'test',
            'body': 'Test',
            'recipient': 'recipient',
        }
        form = PrivateMessageCreationForm(post, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('recipient', errors)
        self.assertEqual(len(errors['recipient']), 1)
        self.assertEqual(errors['recipient'][0].code, 'recipient_has_blocked_user')

    def test_save(self):
        """
        Test the save method of the form.
        """
        sender, recipient = self._get_test_users()
        post = {
            'subject': 'test',
            'body': 'Test',
            'recipient': 'recipient',
        }
        form = PrivateMessageCreationForm(post, sender=sender)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertEqual(list(PrivateMessage.objects.all()), [obj])


class PrivateMessageReplyFormTestCase(TestCase):
    """
    Tests case for the ``PrivateMessageReplyForm`` form.
    """

    def _get_test_users(self):
        """
        Return some test users.
        """
        sender = get_user_model().objects.create_user(username='sender',
                                                      password='illpassword',
                                                      email='sender@example.com')
        recipient = get_user_model().objects.create_user(username='recipient',
                                                         password='illpassword',
                                                         email='recipient@example.com')
        return sender, recipient

    def test_init(self):
        """
        Test the form creation and initial values.
        """
        sender, recipient = self._get_test_users()
        parent_msg = PrivateMessage.objects.create(sender=sender,
                                                   recipient=recipient,
                                                   subject='Test message',
                                                   body='Test message')
        form = PrivateMessageReplyForm(parent_msg=parent_msg, sender=sender)
        self.assertEqual(sender, form.sender)
        self.assertEqual(parent_msg, form.parent_msg)

        self.assertEqual(_re_subject(parent_msg.subject), form.fields['subject'].initial)
        self.assertTrue(form.fields['body'].initial)  # Simple test for something

    def test_do_not_disturb_recipient(self):
        """
        Test if the form raise a validation error if a recipient who do not accept private message is set.
        """
        sender, recipient = self._get_test_users()
        recipient.privatemsg_profile.accept_privmsg = False
        recipient.privatemsg_profile.save()
        parent_msg = PrivateMessage.objects.create(sender=recipient,
                                                   recipient=sender,
                                                   subject='Test message',
                                                   body='Test message')
        post = {
            'subject': 'test',
            'body': 'Test',
        }
        form = PrivateMessageReplyForm(post, parent_msg=parent_msg, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('__all__', errors)
        self.assertEqual(len(errors['__all__']), 1)
        self.assertEqual(errors['__all__'][0].code, 'recipient_refuse_privatemsg')

    def test_blocked_by_recipient(self):
        """
        Test if the form raise a validation error if the recipient has block the sender is set.
        """
        sender, recipient = self._get_test_users()
        BlockedUser.objects.create(user=recipient, blocked_user=sender)
        parent_msg = PrivateMessage.objects.create(sender=recipient,
                                                   recipient=sender,
                                                   subject='Test message',
                                                   body='Test message')
        post = {
            'subject': 'test',
            'body': 'Test',
        }
        form = PrivateMessageReplyForm(post, parent_msg=parent_msg, sender=sender)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('__all__', errors)
        self.assertEqual(len(errors['__all__']), 1)
        self.assertEqual(errors['__all__'][0].code, 'recipient_has_blocked_user')

    def test_save(self):
        """
        Test the save method of the form.
        """
        sender, recipient = self._get_test_users()
        parent_msg = PrivateMessage.objects.create(sender=sender,
                                                   recipient=recipient,
                                                   subject='Test message',
                                                   body='Test message')
        post = {
            'subject': 'test',
            'body': 'Test',
        }
        form = PrivateMessageReplyForm(post, parent_msg=parent_msg, sender=sender)
        self.assertTrue(form.is_valid())

        obj = form.save()
        self.assertEqual(list(PrivateMessage.objects.all()), [obj, parent_msg])
