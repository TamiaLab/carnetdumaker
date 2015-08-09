"""
Test suite for the views of the user accounts app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings


class UserAccountsViewsTestCase(TestCase):
    """
    Test suite for the views.
    """

    def setUp(self):
        """
        Create a new user named "johndoe" with password "illpassword".
        """
        get_user_model().objects.create_user(username='johndoe',
                                             password='illpassword',
                                             email='john.doe@example.com')

    def test_accounts_list_view_available(self):
        """
        Test the availability of the "accounts list" view.
        """
        client = Client()
        response = client.get(reverse('accounts:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/accounts_list.html')

    def test_my_account_view_redirect_not_login(self):
        """
        Test the redirection of the "my account" view when not logged-in.
        """
        client = Client()
        myaccount_url = reverse('myaccount:index')
        response = client.get(myaccount_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, myaccount_url))

    def test_my_account_view_available(self):
        """
        Test the availability of the "my account" view when logged-in.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('myaccount:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/my_account.html')

    def test_password_change_redirect_not_login(self):
        """
        Test the redirect of the "change password" view when not logged-in.
        """
        client = Client()
        password_change_url = reverse('myaccount:password_change')
        response = client.get(password_change_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, password_change_url))

    def test_password_change_view_available(self):
        """
        Test the availability of the "change password" view when logged-in.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('myaccount:password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_change_form.html')

    def test_password_change_done_redirect_not_login(self):
        """
        Test the redirect of the "change password done" view when not logged-in.
        """
        client = Client()
        password_change_done_url = reverse('myaccount:password_change_done')
        response = client.get(password_change_done_url)
        self.assertRedirects(response, '%s?next=%s' % (settings.LOGIN_URL, password_change_done_url))

    def test_password_change_done_view_available(self):
        """
        Test the availability of the "password changed" view when logged-in.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('myaccount:password_change_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_change_done.html')

    def test_public_user_account_view_available(self):
        """
        Test the availability of the "public user account" view.
        """
        client = Client()
        response = client.get(reverse('accounts:user_profile', kwargs={'username': 'johndoe'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/public_user_account.html')

    def test_public_user_account_view_invalid_username(self):
        """
        Test the non-availability of the "public user account" view when user don't exist.
        """
        client = Client()
        response = client.get(reverse('accounts:user_profile', kwargs={'username': 'invalid'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_public_user_account_view_inactive_user(self):
        """
        Test the non-availability of the "public user account" view when user is inactive.
        """
        user = get_user_model().objects.create_user(username='inactive',
                                                    password='illpassword',
                                                    email='inactive@example.com')
        user.is_active = False
        user.save()
        client = Client()
        response = client.get(reverse('accounts:user_profile', kwargs={'username': 'inactive'}))
        self.assertEqual(response.status_code, 410)
        self.assertTemplateUsed(response, 'accounts/public_user_account.html')
