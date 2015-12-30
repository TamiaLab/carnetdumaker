"""
Tests suite for the views of the bug tracker app.
"""

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import (IssueTicket,
                      IssueComment,
                      IssueChange,
                      IssueTicketSubscription)


class BugTrackerViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_user(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')
        self.ticket = IssueTicket.objects.create(title='Test ticket 1',
                                                 description='Test',
                                                 submitter=self.user,
                                                 assigned_to=self.user)
        self.comment = IssueComment.objects.create(issue=self.ticket,
                                                   author=self.user,
                                                   body='Test comment')
        self.change = IssueChange.objects.create(issue=self.ticket,
                                                 comment=self.comment,
                                                 field_name='status',
                                                 old_value='test',
                                                 new_value='test2')
        self.subscription = IssueTicketSubscription.objects.create(issue=self.ticket,
                                                                   user=self.user)

    def test_index_view_available(self):
        """
        Test the availability of the "index" view.
        """
        client = Client()
        response = client.get(reverse('bugtracker:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/bugtracker_index.html')

    def test_tickets_list_view_available(self):
        """
        Test the availability of the "ticket list" view.
        """
        client = Client()
        response = client.get(reverse('bugtracker:issues_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_list.html')
        self.assertIn('issues', response.context)
        self.assertQuerysetEqual(response.context['issues'], ['<IssueTicket: Test ticket 1>'])

    def test_tickets_list_has_comment_subscribe_flags(self):
        """
        Test the redirection of the "ticket list" view when logged-in.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issues_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_list.html')
        self.assertIn('issues', response.context)
        self.assertQuerysetEqual(response.context['issues'], ['<IssueTicket: Test ticket 1>'])
        self.assertEqual(response.context['issues'][0].user_comments, [self.comment])
        self.assertEqual(response.context['issues'][0].user_subscriptions, [self.subscription])

    def test_my_tickets_list_view_available(self):
        """
        Test the availability of the "my ticket list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:mytickets_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_mylist.html')
        self.assertIn('issues', response.context)
        self.assertQuerysetEqual(response.context['issues'], ['<IssueTicket: Test ticket 1>'])

    def test_my_tickets_list_view_redirect_not_login(self):
        """
        Test the redirection of the "my ticket list" view when not logged-in.
        """
        client = Client()
        mytickets_url = reverse('bugtracker:mytickets_list')
        response = client.get(mytickets_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, mytickets_url))

    def test_ticket_create_view_available(self):
        """
        Test the availability of the "open new ticket" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_form.html')

    def test_ticket_create_view_redirect_not_login(self):
        """
        Test the availability of the "open new ticket" view when logged-in.
        """
        client = Client()
        newticket_url = reverse('bugtracker:issue_create')
        response = client.get(newticket_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, newticket_url))

    def test_ticket_show_view_available(self):
        """
        Test the availability of the "ticket detail" view.
        """
        client = Client()
        response = client.get(reverse('bugtracker:issue_detail', kwargs={'pk': self.ticket.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_detail.html')
        self.assertIn('issue', response.context)
        self.assertEqual(response.context['issue'], self.ticket)
        self.assertIn('has_subscribe_to_issue', response.context)
        self.assertFalse(response.context['has_subscribe_to_issue'])
        self.assertIn('is_flooding', response.context)
        self.assertFalse(response.context['is_flooding'])

    def test_ticket_show_view_available_login(self):
        """
        Test the availability of the "ticket detail" view when logged-in.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_detail', kwargs={'pk': self.ticket.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_detail.html')
        self.assertIn('issue', response.context)
        self.assertEqual(response.context['issue'], self.ticket)
        self.assertIn('has_subscribe_to_issue', response.context)
        self.assertTrue(response.context['has_subscribe_to_issue'])
        self.assertIn('is_flooding', response.context)
        self.assertFalse(response.context['is_flooding'])

    def test_ticket_show_unknown_id(self):
        """
        Test the un-availability of the "ticket detail" view with an unknown ticket ID.
        """
        client = Client()
        response = client.get(reverse('bugtracker:issue_detail', kwargs={'pk': '404'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_ticket_edit_view_available(self):
        """
        Test the availability of the "edit ticket" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_edit', kwargs={'pk': self.ticket.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_edit.html')
        self.assertIn('issue', response.context)
        self.assertEqual(response.context['issue'], self.ticket)

    def test_ticket_edit_view_redirect_not_login(self):
        """
        Test the redirection of the "edit ticket" view when not logged-in.
        """
        client = Client()
        editticket_url = reverse('bugtracker:issue_edit', kwargs={'pk': self.ticket.pk})
        response = client.get(editticket_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, editticket_url))

    def test_ticket_edit_unknown_id(self):
        """
        Test the un-availability of the "edit ticket" view with an unknown ticket ID.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_edit', kwargs={'pk': '404'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_ticket_edit_not_permitted(self):
        """
        Test the un-availability of the "edit ticket" view when user don't have the right to edit the ticket.
        """
        get_user_model().objects.create_user(username='johnsmith',
                                             password='illpassword',
                                             email='john.smith@example.com')
        client = Client()
        client.login(username='johnsmith', password='illpassword')
        response = client.get(reverse('bugtracker:issue_edit', kwargs={'pk': self.ticket.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

    def test_ticket_subscribe_view_available(self):
        """
        Test the availability of the "subscribe" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_subscribe', kwargs={'pk': self.ticket.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_subscribe.html')
        self.assertIn('issue', response.context)
        self.assertEqual(response.context['issue'], self.ticket)

    def test_ticket_subscribe_view_redirect_not_login(self):
        """
        Test the redirection of the "subscribe" view when not logged-in.
        """
        client = Client()
        subscribe_url = reverse('bugtracker:issue_subscribe', kwargs={'pk': self.ticket.pk})
        response = client.get(subscribe_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, subscribe_url))

    def test_ticket_subscribe_unknown_id(self):
        """
        Test the un-availability of the "subscribe" view with an unknown ticket ID.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_subscribe', kwargs={'pk': '404'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_ticket_unsubscribe_view_available(self):
        """
        Test the availability of the "un-subscribe" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_unsubscribe', kwargs={'pk': self.ticket.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_unsubscribe.html')
        self.assertIn('issue', response.context)
        self.assertEqual(response.context['issue'], self.ticket)

    def test_ticket_unsubscribe_view_redirect_not_login(self):
        """
        Test the redirection of the "un-subscribe" view when not logged-in.
        """
        client = Client()
        unsubscribe_url = reverse('bugtracker:issue_unsubscribe', kwargs={'pk': self.ticket.pk})
        response = client.get(unsubscribe_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, unsubscribe_url))

    def test_ticket_unsubscribe_unknown_id(self):
        """
        Test the un-availability of the "un-subscribe" view with an unknown ticket ID.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:issue_unsubscribe', kwargs={'pk': '404'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_comment_show_redirect(self):
        """
        Test the redirection of the "comment detail" view with a valid comment ID.
        """
        client = Client()
        comment_url = reverse('bugtracker:comment_detail', kwargs={'pk': self.comment.pk})
        response = client.get(comment_url)
        self.assertRedirects(response, self.comment.get_absolute_url(), status_code=301)

    def test_comment_show_unknown_id(self):
        """
        Test the un-availability of the "comment detail" view with an unknown ticket ID.
        """
        client = Client()
        response = client.get(reverse('bugtracker:comment_detail', kwargs={'pk': '404'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_my_account_show_view_available(self):
        """
        Test the availability of the "my account" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:myaccount'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/my_account.html')

    def test_my_account_show_view_redirect_not_login(self):
        """
        Test the redirection of the "" view when not logged-in.
        """
        client = Client()
        myaccount_url = reverse('bugtracker:myaccount')
        response = client.get(myaccount_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, myaccount_url))

    def test_my_ticket_subscription_list_view_available(self):
        """
        Test the availability of the "my ticket subscriptions" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('bugtracker:myticketsubscribtions_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bugtracker/issueticket_mysubscriptionslist.html')
        self.assertIn('subscriptions', response.context)
        self.assertEqual(list(response.context['subscriptions']), [self.subscription])

    def test_my_ticket_subscription_list_view_redirect_not_login(self):
        """
        Test the redirection of the "my ticket subscriptions" view when not logged-in.
        """
        client = Client()
        mysubscription_url = reverse('bugtracker:myticketsubscribtions_list')
        response = client.get(mysubscription_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, mysubscription_url))
