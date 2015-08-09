"""
Test suite for the admin views of the user accounts app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model


class UserProfileAdminTestCase(TestCase):
    """
    Test suite for the admin views.
    """

    def setUp(self):
        """
        Create a new super user named "johndoe" with password "illpassword".
        """
        user = get_user_model().objects.create_superuser(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')
        self.profile = user.user_profile
        self.assertIsNotNone(self.profile)

    def test_accounts_list_view_available(self):
        """
        Test the availability of the "accounts list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:accounts_userprofile_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_account_edit_view_available(self):
        """
        Test the availability of the "edit account" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:accounts_userprofile_change', args=[self.profile.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/accounts/change_form.html')
