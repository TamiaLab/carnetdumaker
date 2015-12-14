"""
Tests suite for the views of the log watcher app.
"""

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import LogEvent
from ..constants import (LOG_EVENT_LOGIN_SUCCESS,
                         LOG_EVENT_LOGIN_FAILED,
                         LOG_EVENT_LOGOUT)


class LogWatcherViewsTestCase(TestCase):
    """
    Tests case for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """

        # Create some test fixtures.
        self.user = get_user_model().objects.create_user(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')
        LogEvent.objects.create(type=LOG_EVENT_LOGIN_SUCCESS, username='foobar', ip_address='127.0.0.1')
        LogEvent.objects.create(type=LOG_EVENT_LOGIN_SUCCESS, username='johncraft', ip_address='127.0.0.1')
        LogEvent.objects.create(type=LOG_EVENT_LOGOUT, username='johndoe', ip_address='127.0.0.1')
        LogEvent.objects.create(type=LOG_EVENT_LOGIN_FAILED, username='johndoe', ip_address='127.0.0.1')

    def test_log_events_view_available(self):
        """
        Test the availability of the "log events history" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('loginwatcher:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loginwatcher/events_history.html')
        self.assertIn('events', response.context)
        self.assertEqual(3, len(response.context['events']))
        for event in response.context['events']:
            self.assertEqual('johndoe', event.username)

    def test_log_events_view_redirect_not_login(self):
        """
        Test the redirection of the "log events history" view when the user is not logged in.
        """
        client = Client()
        change_email_url = reverse('loginwatcher:index')
        response = client.get(change_email_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, change_email_url))
