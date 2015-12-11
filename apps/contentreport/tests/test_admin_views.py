"""
Tests suite for the admin views of the content report app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import ContentReport


class ContentReportAdminViewsTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        author = get_user_model().objects.create_superuser(username='johndoe',
                                                           password='illpassword',
                                                           email='john.doe@example.com')
        self.report = ContentReport.objects.create(content_object=author,
                                                   reporter=author,
                                                   reason='Because I can',
                                                   reporter_ip_address='127.0.0.1')

    def test_reports_list_view_available(self):
        """
        Test the availability of the "content reports list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:contentreport_contentreport_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_report_edit_view_available(self):
        """
        Test the availability of the "edit content report" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:contentreport_contentreport_change', args=[self.report.pk]))
        self.assertEqual(response.status_code, 200)
