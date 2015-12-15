"""
Tests suite for the data models of the log watch app.
"""

from unittest.mock import patch
from datetime import timedelta

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import LogEvent
from ..settings import LOG_EVENT_TTL_TIMEOUT_DAYS
from ..constants import (LOG_EVENT_LOGIN_SUCCESS,
                         LOG_EVENT_LOGIN_FAILED,
                         LOG_EVENT_LOGOUT)


class LogEventModelTestCase(TestCase):
    """
    Tests suite for the ``LogEvent`` data model class.
    """

    def _get_event(self):
        """
        Create a new event for testing.
        :return: The newly created event.
        """
        return LogEvent.objects.create(type=LOG_EVENT_LOGIN_SUCCESS,
                                       username='johndoe',
                                       ip_address='10.0.0.56')

    def test_str_method(self):
        event = self._get_event()

        event.type = LOG_EVENT_LOGIN_SUCCESS
        excepted_str = "[%s] LOGIN_SUCCESS %s from %s" % (event.event_date.isoformat(' '),
                                                          event.username, event.ip_address)
        self.assertEqual(excepted_str, str(event))

        event.type = LOG_EVENT_LOGIN_FAILED
        excepted_str = "[%s] LOGIN_FAILED %s from %s" % (event.event_date.isoformat(' '),
                                                         event.username, event.ip_address)
        self.assertEqual(excepted_str, str(event))

        event.type = LOG_EVENT_LOGOUT
        excepted_str = "[%s] LOGOUT %s from %s" % (event.event_date.isoformat(' '),
                                                   event.username, event.ip_address)
        self.assertEqual(excepted_str, str(event))

    def test_ordering(self):
        event1 = LogEvent.objects.create(type=LOG_EVENT_LOGIN_SUCCESS,
                                       username='johndoe',
                                       ip_address='10.0.0.56')
        event2 = LogEvent.objects.create(type=LOG_EVENT_LOGOUT,
                                       username='johndoe',
                                       ip_address='10.0.0.56')
        queryset_events = LogEvent.objects.all()
        self.assertQuerysetEqual(queryset_events, [repr(event2), repr(event1)])

    def test_handle_user_login_success(self):
        """
        Test if login success events are correctly handled.
        """
        get_user_model().objects.create_user(username='johndoe',
                                             password='johndoe',
                                             email='johndoe@example.com')
        nb_events = LogEvent.objects.count()
        self.assertEqual(nb_events, 0)

        client = Client(REMOTE_ADDR='10.0.0.2')
        # client.login() and REMOTE_ADDR does not work together
        client.post(reverse('auth:login'), {'username': 'johndoe', 'password': 'johndoe'})

        nb_events = LogEvent.objects.count()
        self.assertEqual(nb_events, 1)

        event = LogEvent.objects.last()
        self.assertEqual(event.type, LOG_EVENT_LOGIN_SUCCESS)
        self.assertEqual(event.username, 'johndoe')
        self.assertEqual(event.ip_address, '10.0.0.2')

    def test_handle_user_login_failed(self):
        """
        Test if failed login events are correctly handled.
        """
        nb_events = LogEvent.objects.count()
        self.assertEqual(nb_events, 0)

        client = Client(REMOTE_ADDR='10.0.0.2')
        # client.login() and REMOTE_ADDR does not work together
        client.post(reverse('auth:login'), {'username': 'notjohndoe', 'password': 'notjohndoe'})

        nb_events = LogEvent.objects.count()
        self.assertEqual(nb_events, 1)

        event = LogEvent.objects.last()
        self.assertEqual(event.type, LOG_EVENT_LOGIN_FAILED)
        self.assertEqual(event.username, 'notjohndoe')
        self.assertEqual(event.ip_address, None)

    def test_handle_user_logout(self):
        """
        Test if logout events are correctly handled.
        """
        get_user_model().objects.create_user(username='johndoe',
                                             password='johndoe',
                                             email='johndoe@example.com')
        client = Client(REMOTE_ADDR='10.0.0.2')
        # client.login() and REMOTE_ADDR does not work together
        client.post(reverse('auth:login'), {'username': 'johndoe', 'password': 'johndoe'})

        nb_events = LogEvent.objects.count()
        self.assertEqual(nb_events, 1)

        # client.logout() and REMOTE_ADDR does not work together
        client.post(reverse('auth:logout'))
        nb_events = LogEvent.objects.count()
        self.assertEqual(nb_events, 2)

        event = LogEvent.objects.order_by('event_date').last()
        self.assertEqual(event.type, LOG_EVENT_LOGOUT)
        self.assertEqual(event.username, 'johndoe')
        self.assertEqual(event.ip_address, '10.0.0.2')

    def test_handle_user_logout_no_user(self):
        """
        Test if logout events are correctly handled when user was not login before logout.
        """
        client = Client()
        client.logout()
        nb_events = LogEvent.objects.count()
        self.assertEqual(nb_events, 0)

    def test_delete_old_events_method(self):
        """
        Test the ``delete_old_events`` method of the manager class.
        """
        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            e1 = LogEvent.objects.create(type=LOG_EVENT_LOGIN_SUCCESS,
                                         username='johndoe',
                                         ip_address='10.0.0.56')

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now - timedelta(days=LOG_EVENT_TTL_TIMEOUT_DAYS)
            e2 = LogEvent.objects.create(type=LOG_EVENT_LOGOUT,
                                         username='johndoe',
                                         ip_address='10.0.0.56')

        self.assertEqual(list(LogEvent.objects.all()), [e1, e2])
        LogEvent.objects.delete_old_events()
        self.assertEqual(list(LogEvent.objects.all()), [e1])
