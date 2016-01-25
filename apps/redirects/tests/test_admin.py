"""
Tests suite for the admin views of the redirect app.
"""

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import Redirection


class RedirectionAdminTestCase(TestCase):
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
        self.redirection = Redirection.objects.create(site_id=settings.SITE_ID,
                                                      old_path='/404/',
                                                      new_path='/page-not-found/')

    def test_redirection_list_view_available(self):
        """
        Test the availability of the "redirection list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:redirects_redirection_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_redirection_edit_view_available(self):
        """
        Test the availability of the "edit redirection" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:redirects_redirection_change', args=[self.redirection.pk]))
        self.assertEqual(response.status_code, 200)
