"""
Tests suite for the admin views of the user strike app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import UserStrike


class UserStrikeAdminTestCase(TestCase):
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
        self.user = get_user_model().objects.create_user(username='johnsmith',
                                                         password='illpassword',
                                                         email='john.smith@example.com')
        self.strike = UserStrike.objects.create(author=self.author,
                                                internal_reason='Test strike',
                                                target_user=self.user)

    def test_strike_list_view_available(self):
        """
        Test the availability of the "user strike list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:userstrike_userstrike_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_strike_edit_view_available(self):
        """
        Test the availability of the "edit user strike" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:userstrike_userstrike_change', args=[self.strike.pk]))
        self.assertEqual(response.status_code, 200)
