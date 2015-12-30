"""
Tests suite for the forms of the bug tracker app.
"""

from unittest.mock import patch

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth import get_user_model

from ..models import (IssueTicket,
                      IssueComment,
                      IssueTicketSubscription)
from ..forms import (IssueTicketCreationForm,
                     IssueCommentCreationForm)


class IssueTicketCreationFormTestCase(TestCase):
    """
    Tests suite for the ``IssueTicketCreationForm`` form.
    """

    def setUp(self):
        """
        Create some test fixtures.
        """
        self.user = get_user_model().objects.create_user(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')

    def test_save_form(self):
        """
        Test if the form save the new ``IssueTicket``.
        """
        post_data = {
            'title': 'Test title',
            'description': 'Test description',
        }
        form = IssueTicketCreationForm(post_data)
        self.assertTrue(form.is_valid())

        self.assertEqual(0, IssueTicket.objects.count())
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        with patch('apps.bugtracker.forms.notify_of_new_issue') as mock_notify_of_new_issue:
            form.save(request, self.user)

        self.assertEqual(1, IssueTicket.objects.count())
        ticket = IssueTicket.objects.last()
        mock_notify_of_new_issue.assert_called_once_with(ticket, request, self.user)
        self.assertEqual('Test title', ticket.title)
        self.assertEqual('Test description', ticket.description)
        self.assertEqual(self.user, ticket.submitter)
        self.assertEqual('10.0.0.1', ticket.submitter_ip_address)

        self.assertEqual(0, IssueTicketSubscription.objects.count())

    def test_notify_of_reply(self):
        """
        Test if the form save the new ``IssueTicketSubscription`` when requested.
        """
        post_data = {
            'title': 'Test title',
            'description': 'Test description',
            'notify_of_reply': '1',
        }
        form = IssueTicketCreationForm(post_data)
        self.assertTrue(form.is_valid())

        self.assertEqual(0, IssueTicketSubscription.objects.count())
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        with patch('apps.bugtracker.forms.notify_of_new_issue') as mock_notify_of_new_issue:
            form.save(request, self.user)

        self.assertEqual(1, IssueTicketSubscription.objects.count())
        ticket = IssueTicket.objects.last()
        mock_notify_of_new_issue.assert_called_once_with(ticket, request, self.user)
        subscription = IssueTicketSubscription.objects.last()
        self.assertEqual(self.user, subscription.user)
        self.assertEqual(ticket, subscription.issue)
        self.assertTrue(subscription.active)


class IssueCommentCreationFormTestCase(TestCase):
    """
    Tests suite for the ``IssueCommentCreationForm`` form.
    """

    def setUp(self):
        """
        Create some test fixtures.
        """
        self.user = get_user_model().objects.create_user(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')
        self.ticket = IssueTicket.objects.create(title='Test ticket',
                                                 description='Test',
                                                 submitter=self.user,
                                                 assigned_to=self.user)

    def test_save_form(self):
        """
        Test if the form save the new ``IssueTicket``.
        """
        post_data = {
            'comment_body': 'Test body',
        }
        form = IssueCommentCreationForm(post_data)
        self.assertTrue(form.is_valid())

        self.assertEqual(0, IssueComment.objects.count())
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        with patch('apps.bugtracker.forms.notify_of_new_comment') as mock_notify_of_new_comment:
            form.save(request, self.ticket, self.user)

        self.assertEqual(1, IssueComment.objects.count())
        comment = IssueComment.objects.last()
        mock_notify_of_new_comment.assert_called_once_with(self.ticket, comment, request, self.user)
        self.assertEqual(self.ticket, comment.issue)
        self.assertEqual('Test body', comment.body)
        self.assertEqual(self.user, comment.author)
        self.assertEqual('10.0.0.1', comment.author_ip_address)

        self.assertEqual(0, IssueTicketSubscription.objects.count())

    def test_notify_of_reply(self):
        """
        Test if the form save the new ``IssueTicketSubscription`` when requested.
        """
        post_data = {
            'comment_body': 'Test body',
            'notify_of_reply': '1',
        }
        form = IssueCommentCreationForm(post_data)
        self.assertTrue(form.is_valid())

        self.assertEqual(0, IssueTicketSubscription.objects.count())
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        with patch('apps.bugtracker.forms.notify_of_new_comment') as mock_notify_of_new_comment:
            form.save(request, self.ticket, self.user)

        self.assertEqual(1, IssueTicketSubscription.objects.count())
        comment = IssueComment.objects.last()
        mock_notify_of_new_comment.assert_called_once_with(self.ticket, comment, request, self.user)
        subscription = IssueTicketSubscription.objects.last()
        self.assertEqual(self.user, subscription.user)
        self.assertEqual(self.ticket, subscription.issue)
        self.assertTrue(subscription.active)

    def test_unnotify_of_reply(self):
        """
        Test if the form delete the existing ``IssueTicketSubscription`` when requested.
        """
        post_data = {
            'comment_body': 'Test body',
        }
        form = IssueCommentCreationForm(post_data)
        self.assertTrue(form.is_valid())

        IssueTicketSubscription.objects.create(user=self.user, issue=self.ticket)
        self.assertEqual(1, IssueTicketSubscription.objects.count())
        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        with patch('apps.bugtracker.forms.notify_of_new_comment') as mock_notify_of_new_comment:
            form.save(request, self.ticket, self.user)

        self.assertEqual(1, IssueTicketSubscription.objects.count())
        comment = IssueComment.objects.last()
        mock_notify_of_new_comment.assert_called_once_with(self.ticket, comment, request, self.user)
        subscription = IssueTicketSubscription.objects.last()
        self.assertEqual(self.user, subscription.user)
        self.assertEqual(self.ticket, subscription.issue)
        self.assertFalse(subscription.active)
