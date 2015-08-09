"""
Test suite for the views of the content report app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import ContentReport


class ContentReportViewsTestCase(TestCase):
    """
    Test suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_user(username='johndoe',
                                                           password='illpassword',
                                                           email='john.doe@example.com')
        self.report = ContentReport.objects.create(content_object=self.author,
                                                   reporter=self.author,
                                                   reason='Because I can',
                                                   reporter_ip_address='127.0.0.1')

    def test_report_done_view_available(self):
        """
        Test the availability of the "report done" view.
        """
        client = Client()
        response = client.get(reverse('contentreport:content_report_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contentreport/content_report_done.html')
