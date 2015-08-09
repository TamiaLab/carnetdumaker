"""
Tests suite for the admin views of the log watcher app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import LogEvent
from ..constants import LOG_EVENT_LOGIN_FAILED


class LogEventAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_superuser(username='johndoe',
                                                                password='illpassword',
                                                                email='john.doe@example.com')
        self.event = LogEvent.objects.create(type=LOG_EVENT_LOGIN_FAILED,
                                             username='jean.kevin',
                                             ip_address='10.0.0.12')

    def test_log_event_list_view_available(self):
        """
        Test the availability of the "log event list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:loginwatcher_logevent_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_log_event_edit_view_available(self):
        """
        Test the availability of the "edit log event" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:loginwatcher_logevent_change', args=[self.event.pk]))
        self.assertEqual(response.status_code, 200)
