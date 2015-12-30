"""
Tests suite for the models of the bug tracker app.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


from ..models import (AppComponent,
                      IssueTicket,
                      IssueComment,
                      IssueChange,
                      IssueTicketSubscription,
                      BugTrackerUserProfile)
from ..constants import (STATUS_OPEN,
                         STATUS_CLOSED,
                         PRIORITY_NEED_REVIEW,
                         PRIORITY_GODZILLA,
                         DIFFICULTY_NORMAL,
                         DIFFICULTY_IMPORTANT)
from ..settings import (NB_ISSUE_COMMENTS_PER_PAGE,
                        NB_SECONDS_BETWEEN_COMMENTS)


class AppComponentTestCase(TestCase):
    """
    Tests suite for the ``AppComponent`` data model class.
    """

    def test_str(self):
        """
        Test the ``__str__`` method of the model.
        """
        component = AppComponent.objects.create(name='Test',
                                                internal_name='iTest',
                                                description='Test app')
        self.assertEqual(component.name, str(component))


class IssueTicketTestCase(TestCase):
    """
    Tests suite for the ``IssueTicket`` data model class.
    """

    def _get_ticket(self):
        """
        Create some test fixtures.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket',
                                            description='Test',
                                            submitter=user)
        return user, ticket

    def test_default_values(self):
        """
        Test default values of the model.
        """
        user, ticket = self._get_ticket()
        self.assertIsNone(ticket.component)
        self.assertIsNotNone(ticket.submission_date)
        self.assertIsNotNone(ticket.last_modification_date)
        self.assertIsNone(ticket.assigned_to)
        self.assertEqual(STATUS_OPEN, ticket.status)
        self.assertEqual(PRIORITY_NEED_REVIEW, ticket.priority)
        self.assertEqual(DIFFICULTY_NORMAL, ticket.difficulty)

    def test_str(self):
        """
        Test the ``__str__`` method of the model.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(ticket.title, str(ticket))

    def test_get_absolute_url_method(self):
        """
        Test the ``get_absolute_url`` method of the model.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(ticket.get_absolute_url(),
                         reverse('bugtracker:issue_detail', kwargs={'pk': ticket.pk}))

    def test_get_edit_url_method(self):
        """
        Test the ``get_edit_url`` method of the model.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(ticket.get_edit_url(),
                         reverse('bugtracker:issue_edit', kwargs={'pk': ticket.pk}))

    def test_get_subscribe_url_method(self):
        """
        Test the ``get_subscribe_url`` method of the model.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(ticket.get_subscribe_url(),
                         reverse('bugtracker:issue_subscribe', kwargs={'pk': ticket.pk}))

    def test_get_unsubscribe_url_method(self):
        """
        Test the ``get_unsubscribe_url`` method of the model.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(ticket.get_unsubscribe_url(),
                         reverse('bugtracker:issue_unsubscribe', kwargs={'pk': ticket.pk}))

    def test_get_latest_comments_rss_feed_url_method(self):
        """
        Test the ``get_unsubscribe_url`` method of the model.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(ticket.get_latest_comments_rss_feed_url(),
                         reverse('bugtracker:latest_issue_comments_for_issue_rss', kwargs={'pk': ticket.pk}))

    def test_get_latest_comments_atom_feed_url_method(self):
        """
        Test the ``get_latest_comments_atom_feed_url`` method of the model.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(ticket.get_latest_comments_atom_feed_url(),
                         reverse('bugtracker:latest_issue_comments_for_issue_rss', kwargs={'pk': ticket.pk}))

    def test_create_revision_without_extra_on_component_change(self):
        """
        Test the creation of a ticket revision without extra information upon component change.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(0, IssueComment.objects.count())
        self.assertEqual(0, IssueChange.objects.count())
        ticket.component = AppComponent.objects.create(name='Test',
                                                       internal_name='iTest',
                                                       description='Test app')
        ticket.save()

        self.assertEqual(1, IssueComment.objects.count())
        comment = IssueComment.objects.last()
        self.assertEqual(ticket, comment.issue)
        self.assertEqual(user, comment.author)
        self.assertEqual('', comment.body)
        self.assertIsNone(comment.author_ip_address)

        self.assertEqual(1, IssueChange.objects.count())
        change = IssueChange.objects.last()
        self.assertEqual(ticket, change.issue)
        self.assertEqual(comment, change.comment)
        self.assertEqual('component', change.field_name)
        self.assertEqual('', change.old_value)
        self.assertEqual('iTest', change.new_value)

    def test_create_revision_without_extra_on_assigned_to_change(self):
        """
        Test the creation of a ticket revision without extra information upon "assigned_to" change.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(0, IssueComment.objects.count())
        self.assertEqual(0, IssueChange.objects.count())
        ticket.assigned_to = get_user_model().objects.create_user(username='johndoe2',
                                                                  password='illpassword',
                                                                  email='john.doe2@example.com')
        ticket.save()

        self.assertEqual(1, IssueComment.objects.count())
        comment = IssueComment.objects.last()
        self.assertEqual(ticket, comment.issue)
        self.assertEqual(user, comment.author)
        self.assertEqual('', comment.body)
        self.assertIsNone(comment.author_ip_address)

        self.assertEqual(1, IssueChange.objects.count())
        change = IssueChange.objects.last()
        self.assertEqual(ticket, change.issue)
        self.assertEqual(comment, change.comment)
        self.assertEqual('assigned_to', change.field_name)
        self.assertEqual('', change.old_value)
        self.assertEqual('johndoe2', change.new_value)

    def test_create_revision_without_extra_on_status_change(self):
        """
        Test the creation of a ticket revision without extra information upon "status" change.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(0, IssueComment.objects.count())
        self.assertEqual(0, IssueChange.objects.count())
        ticket.status = STATUS_CLOSED
        ticket.save()

        self.assertEqual(1, IssueComment.objects.count())
        comment = IssueComment.objects.last()
        self.assertEqual(ticket, comment.issue)
        self.assertEqual(user, comment.author)
        self.assertEqual('', comment.body)
        self.assertIsNone(comment.author_ip_address)

        self.assertEqual(1, IssueChange.objects.count())
        change = IssueChange.objects.last()
        self.assertEqual(ticket, change.issue)
        self.assertEqual(comment, change.comment)
        self.assertEqual('status', change.field_name)
        self.assertEqual('open', change.old_value)
        self.assertEqual('closed', change.new_value)

    def test_create_revision_without_extra_on_priority_change(self):
        """
        Test the creation of a ticket revision without extra information upon "priority" change.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(0, IssueComment.objects.count())
        self.assertEqual(0, IssueChange.objects.count())
        ticket.priority = PRIORITY_GODZILLA
        ticket.save()

        self.assertEqual(1, IssueComment.objects.count())
        comment = IssueComment.objects.last()
        self.assertEqual(ticket, comment.issue)
        self.assertEqual(user, comment.author)
        self.assertEqual('', comment.body)
        self.assertIsNone(comment.author_ip_address)

        self.assertEqual(1, IssueChange.objects.count())
        change = IssueChange.objects.last()
        self.assertEqual(ticket, change.issue)
        self.assertEqual(comment, change.comment)
        self.assertEqual('priority', change.field_name)
        self.assertEqual('needreview', change.old_value)
        self.assertEqual('godzilla', change.new_value)

    def test_create_revision_without_extra_on_difficulty_change(self):
        """
        Test the creation of a ticket revision without extra information upon "difficulty" change.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(0, IssueComment.objects.count())
        self.assertEqual(0, IssueChange.objects.count())
        ticket.difficulty = DIFFICULTY_IMPORTANT
        ticket.save()

        self.assertEqual(1, IssueComment.objects.count())
        comment = IssueComment.objects.last()
        self.assertEqual(ticket, comment.issue)
        self.assertEqual(user, comment.author)
        self.assertEqual('', comment.body)
        self.assertIsNone(comment.author_ip_address)

        self.assertEqual(1, IssueChange.objects.count())
        change = IssueChange.objects.last()
        self.assertEqual(ticket, change.issue)
        self.assertEqual(comment, change.comment)
        self.assertEqual('difficulty', change.field_name)
        self.assertEqual('normal', change.old_value)
        self.assertEqual('important', change.new_value)

    def test_create_revision_with_extra(self):
        """
        Test the creation of a ticket revision with extra information.
        """
        user, ticket = self._get_ticket()
        self.assertEqual(0, IssueComment.objects.count())
        self.assertEqual(0, IssueChange.objects.count())
        ticket.difficulty = DIFFICULTY_IMPORTANT
        ticket.save(changes_comment='Test change',
                    changes_author=user,
                    changes_author_ip_address='10.0.0.1')

        self.assertEqual(1, IssueComment.objects.count())
        comment = IssueComment.objects.last()
        self.assertEqual(ticket, comment.issue)
        self.assertEqual(user, comment.author)
        self.assertEqual('Test change', comment.body)
        self.assertEqual('10.0.0.1', comment.author_ip_address)

        self.assertEqual(1, IssueChange.objects.count())
        change = IssueChange.objects.last()
        self.assertEqual(ticket, change.issue)
        self.assertEqual(comment, change.comment)
        self.assertEqual('difficulty', change.field_name)
        self.assertEqual('normal', change.old_value)
        self.assertEqual('important', change.new_value)

    def test_can_edit_submitter(self):
        """
        Test the ``can_edit`` method of the model with the submitter itself.
        """
        user, ticket = self._get_ticket()
        self.assertTrue(ticket.can_edit(user))

    def test_can_edit_authorized(self):
        """
        Test the ``can_edit`` method of the model with an authorized user.
        """
        user, ticket = self._get_ticket()
        authorized_user = get_user_model().objects.create_user(username='jonhsmith',
                                                               password='jonhsmith',
                                                               email='jonh.smith@example.com')
        content_type = ContentType.objects.get_for_model(IssueTicket)
        permission = Permission.objects.get(codename='change_issueticket', content_type=content_type)
        authorized_user.user_permissions.add(permission)

        self.assertNotEqual(ticket.submitter, authorized_user)
        self.assertTrue(ticket.can_edit(authorized_user))

    def test_can_edit_anonymous(self):
        """
        Test the ``can_edit`` method of the model with an anonymous user.
        """
        user, ticket = self._get_ticket()
        anonymous = get_user_model().objects.create_user(username='jonhsmith',
                                                         password='jonhsmith',
                                                         email='jonh.smith@example.com')
        self.assertNotEqual(ticket.submitter, anonymous)
        self.assertFalse(ticket.can_edit(anonymous))


class IssueCommentTestCase(TestCase):
    """
    Tests suite for the ``IssueComment`` data model class.
    """

    def _get_comment(self):
        """
        Create some test fixtures.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket',
                                            description='Test',
                                            submitter=user,
                                            assigned_to=user)
        comment = IssueComment.objects.create(issue=ticket,
                                              author=user,
                                              body='Test comment')
        return user, ticket, comment

    def test_default_values(self):
        """
        Test default values of the model.
        """
        user, ticket, comment = self._get_comment()
        self.assertIsNotNone(comment.pub_date)
        self.assertIsNotNone(comment.last_modification_date)

    def test_str(self):
        """
        Test the ``__str__`` method of the model.
        """
        user, ticket, comment = self._get_comment()
        self.assertEqual('Comment for issue "%s": "%s..."' % (ticket.title, comment.short_body()),
                         str(comment))

    def test_get_absolute_url_method(self):
        """
        Test the ``get_absolute_url`` method of the model.
        """
        user, ticket, comment = self._get_comment()
        self.assertEqual(comment.get_absolute_url(),
                         ticket.get_absolute_url() + '#comment-%d' % comment.id)

    def test_get_absolute_url_method_paginated(self):
        """
        Test the ``get_absolute_url`` method of the model with pagination.
        """
        user, ticket, comment = self._get_comment()
        for i in range(NB_ISSUE_COMMENTS_PER_PAGE - 1):
            comment = IssueComment.objects.create(issue=ticket,
                                                  author=user,
                                                  body='Test comment %d' % i)
        self.assertEqual(comment.get_absolute_url(),
                         ticket.get_absolute_url() + '#comment-%d' % comment.id)

        comment = IssueComment.objects.create(issue=ticket,
                                              author=user,
                                              body='Test first comment page 2')
        self.assertEqual(comment.get_absolute_url(),
                         ticket.get_absolute_url() + '?page=2#comment-%d' % comment.id)

        for i in range(NB_ISSUE_COMMENTS_PER_PAGE - 1):
            comment = IssueComment.objects.create(issue=ticket,
                                                  author=user,
                                                  body='Test comment %d' % i)
        self.assertEqual(comment.get_absolute_url(),
                         ticket.get_absolute_url() + '?page=2#comment-%d' % comment.id)

        comment = IssueComment.objects.create(issue=ticket,
                                              author=user,
                                              body='Test first comment page 3')
        self.assertEqual(comment.get_absolute_url(),
                         ticket.get_absolute_url() + '?page=3#comment-%d' % comment.id)

    def test_get_absolute_url_simple_method(self):
        """
        Test the ``get_absolute_url_simple`` method of the model.
        """
        user, ticket, comment = self._get_comment()
        self.assertEqual(comment.get_absolute_url_simple(),
                         reverse('bugtracker:comment_detail', kwargs={'pk': comment.pk}))

    def test_get_report_url_method(self):
        """
        Test the ``get_report_url`` method of the model.
        """
        user, ticket, comment = self._get_comment()
        self.assertEqual(comment.get_report_url(),
                         reverse('bugtracker:comment_report', kwargs={'pk': comment.pk}))

    def test_short_body_method(self):
        """
        Test the ``get_report_url`` method of the model.
        """
        user, ticket, comment = self._get_comment()
        comment.body_text = "012345678901234567890123456789"
        self.assertEqual('01234567890123456789', comment.short_body())


class IssueTicketSubscriptionTestCase(TestCase):
    """
    Tests suite for the ``IssueTicketSubscription`` data model class.
    """

    def _get_subscription(self):
        """
        Create some test fixtures.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket',
                                            description='Test',
                                            submitter=user,
                                            assigned_to=user)
        subscription = IssueTicketSubscription.objects.create(issue=ticket, user=user)
        return user, ticket, subscription

    def test_str(self):
        """
        Test the ``__str__`` method of the model.
        """
        user, ticket, subscription = self._get_subscription()
        self.assertEqual('Subscription of "%s" for issue #%d' % (user.username, ticket.pk),
                         str(subscription))

    def test_get_subscribers_for_issue_method(self):
        """
        Test the ``get_subscribers_for_issue`` method of the manager class.
        """
        user, ticket, subscription = self._get_subscription()
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                     password='illpassword',
                                                     email='john.doe@example.com')
        IssueTicketSubscription.objects.create(user=user2, issue=ticket, active=False)

        result = IssueTicketSubscription.objects.get_subscribers_for_issue(ticket)
        self.assertQuerysetEqual(result, [repr(subscription)])

    def test_has_subscribed_to_issue_method(self):
        """
        Test the ``has_subscribed_to_issue`` method of the manager class.
        """
        user, ticket, subscription = self._get_subscription()
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                     password='illpassword',
                                                     email='john.doe@example.com')
        IssueTicketSubscription.objects.create(user=user2, issue=ticket, active=False)

        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))

    def test_subscribe_to_issue_method(self):
        """
        Test the ``subscribe_to_issue`` method of the manager class.
        """
        user, ticket, subscription = self._get_subscription()
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                     password='illpassword',
                                                     email='john.doe@example.com')
        IssueTicketSubscription.objects.create(user=user2, issue=ticket, active=False)

        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))

        IssueTicketSubscription.objects.subscribe_to_issue(user2, ticket)

        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))

    def test_subscribe_to_issue_method2(self):
        """
        Test the ``subscribe_to_issue`` method of the manager class (create object).
        """
        user, ticket, subscription = self._get_subscription()
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                     password='illpassword',
                                                     email='john.doe@example.com')

        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))

        IssueTicketSubscription.objects.subscribe_to_issue(user2, ticket)

        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))

    def test_unsubscribe_from_issue_method(self):
        """
        Test the ``unsubscribe_from_issue`` method of the manager class.
        """
        user, ticket, subscription = self._get_subscription()
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                     password='illpassword',
                                                     email='john.doe@example.com')
        IssueTicketSubscription.objects.create(user=user2, issue=ticket, active=False)

        self.assertTrue(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))

        IssueTicketSubscription.objects.unsubscribe_from_issue(user, ticket)

        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))

        IssueTicketSubscription.objects.unsubscribe_from_issue(user2, ticket)

        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user, ticket))
        self.assertFalse(IssueTicketSubscription.objects.has_subscribed_to_issue(user2, ticket))


class BugTrackerUserProfileTestCase(TestCase):
    """
    Tests suite for the ``BugTrackerUserProfile`` data model class.
    """

    def _get_bugtracker_profile(self):
        """
        Create some test fixtures.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        return user, user.bugtracker_profile

    def test_default_values(self):
        """
        Test default values of the model.
        """
        user, bugtracker_profile = self._get_bugtracker_profile()
        self.assertIsNotNone(bugtracker_profile)
        self.assertIsInstance(bugtracker_profile, BugTrackerUserProfile)
        self.assertFalse(bugtracker_profile.notify_of_new_issue)
        self.assertTrue(bugtracker_profile.notify_of_reply_by_default)
        self.assertIsNone(bugtracker_profile.last_comment_date)

    def test_str(self):
        """
        Test the ``__str__`` method of the model.
        """
        user, bugtracker_profile = self._get_bugtracker_profile()
        self.assertEqual('Bugtracker user\'s profile of "%s"' % user.username,
                         str(bugtracker_profile))

    def test_is_flooding_no_last_comment_date(self):
        """
        Test the ``is_flooding`` method of the model with an user who never posting anything.
        """
        user, bugtracker_profile = self._get_bugtracker_profile()
        self.assertIsNone(bugtracker_profile.last_comment_date)
        self.assertFalse(bugtracker_profile.is_flooding())

    def test_is_flooding_not_triggered(self):
        """
        Test the ``is_flooding`` method of the model with a last post date greater than the limit time windows.
        """
        user, bugtracker_profile = self._get_bugtracker_profile()
        now = timezone.now()
        bugtracker_profile.last_comment_date = now - timedelta(seconds=NB_SECONDS_BETWEEN_COMMENTS)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            self.assertFalse(bugtracker_profile.is_flooding())

    def test_is_flooding_triggered(self):
        """
        Test the ``is_flooding`` method of the model with a last post date greater than the limit time windows.
        """
        user, bugtracker_profile = self._get_bugtracker_profile()
        now = timezone.now()
        bugtracker_profile.last_comment_date = now - timedelta(seconds=NB_SECONDS_BETWEEN_COMMENTS - 1)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            self.assertTrue(bugtracker_profile.is_flooding())

    def test_rearm_flooding_delay_and_save_method(self):
        """
        Test the ``rearm_flooding_delay_and_save`` method of the model.
        """
        user, bugtracker_profile = self._get_bugtracker_profile()
        now = timezone.now()
        self.assertIsNone(bugtracker_profile.last_comment_date)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            bugtracker_profile.rearm_flooding_delay_and_save()
        bugtracker_profile.refresh_from_db()
        self.assertEqual(now, bugtracker_profile.last_comment_date)

    def test_get_subscribers_for_new_issue_method(self):
        """
        Test the ``get_subscribers_for_new_issue`` method of the manager class.
        """
        user1 = get_user_model().objects.create_user(username='johndoe1',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        user1.bugtracker_profile.notify_of_new_issue = True
        user1.bugtracker_profile.save()
        user2 = get_user_model().objects.create_user(username='johndoe2',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        user2.bugtracker_profile.notify_of_new_issue = True
        user2.bugtracker_profile.save()
        user3 = get_user_model().objects.create_user(username='johndoe3',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        user3.bugtracker_profile.notify_of_new_issue = False
        user3.bugtracker_profile.save()

        result = BugTrackerUserProfile.objects.get_subscribers_for_new_issue()
        self.assertQuerysetEqual(result,
                                 ['<BugTrackerUserProfile: Bugtracker user\'s profile of "johndoe1">',
                                  '<BugTrackerUserProfile: Bugtracker user\'s profile of "johndoe2">'],
                                 ordered=False)
