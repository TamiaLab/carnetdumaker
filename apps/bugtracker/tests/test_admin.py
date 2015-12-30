"""
Tests suite for the admin views of the bug tracker app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import (AppComponent,
                      IssueTicket,
                      IssueComment,
                      IssueChange,
                      IssueTicketSubscription,
                      BugTrackerUserProfile)


class AppComponentAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_superuser(username='johndoe',
                                                              password='illpassword',
                                                              email='john.doe@example.com')
        self.component = AppComponent.objects.create(name='test',
                                                     internal_name='test-app',
                                                     description='Test component')

    def test_app_component_list_view_available(self):
        """
        Test the availability of the "app component list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_appcomponent_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_app_component_edit_view_available(self):
        """
        Test the availability of the "edit app component" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_appcomponent_change', args=[self.component.pk]))
        self.assertEqual(response.status_code, 200)

class IssueTicketAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_superuser(username='johndoe',
                                                              password='illpassword',
                                                              email='john.doe@example.com')
        self.ticket = IssueTicket.objects.create(title='Test ticket',
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

    def test_issue_ticket_list_view_available(self):
        """
        Test the availability of the "issue ticket list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_issueticket_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_issue_ticket_edit_view_available(self):
        """
        Test the availability of the "edit issue ticket" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_issueticket_change', args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 200)


class IssueCommentAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_superuser(username='johndoe',
                                                              password='illpassword',
                                                              email='john.doe@example.com')
        self.ticket = IssueTicket.objects.create(title='Test ticket',
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

    def test_issue_comment_list_view_available(self):
        """
        Test the availability of the "issue comment list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_issuecomment_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_issue_comment_edit_view_available(self):
        """
        Test the availability of the "edit issue comment" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_issuecomment_change', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 200)


class BugTrackerUserProfileAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_superuser(username='johndoe',
                                                              password='illpassword',
                                                              email='john.doe@example.com')
        self.bgprofile = self.user.bugtracker_profile
        self.assertIsNotNone(self.bgprofile)
        self.assertIsInstance(self.bgprofile, BugTrackerUserProfile)

    def test_bugtracker_profile_list_view_available(self):
        """
        Test the availability of the "bugtracker profile list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_bugtrackeruserprofile_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_bugtracker_profile_edit_view_available(self):
        """
        Test the availability of the "edit bugtracker profile" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_bugtrackeruserprofile_change', args=[self.bgprofile.pk]))
        self.assertEqual(response.status_code, 200)


class IssueTicketSubscriptionAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_superuser(username='johndoe',
                                                              password='illpassword',
                                                              email='john.doe@example.com')
        self.ticket = IssueTicket.objects.create(title='Test ticket',
                                                 description='Test',
                                                 submitter=self.user,
                                                 assigned_to=self.user)
        self.subscription = IssueTicketSubscription.objects.create(issue=self.ticket,
                                                                   user=self.user)

    def test_bugtracker_profile_list_view_available(self):
        """
        Test the availability of the "bugtracker profile list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_issueticketsubscription_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_bugtracker_profile_edit_view_available(self):
        """
        Test the availability of the "edit bugtracker profile" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:bugtracker_issueticketsubscription_change', args=[self.subscription.pk]))
        self.assertEqual(response.status_code, 200)
