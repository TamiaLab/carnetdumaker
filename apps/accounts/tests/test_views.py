"""
Tests suite for the views of the user accounts app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings


class UserAccountsViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create a new user named "johndoe" with password "illpassword" and some test users.
        """
        self.user_1 = get_user_model().objects.create_user(username='johndoe1',
                                                           password='illpassword',
                                                           email='johndoe1@example.com')
        self.assertIsNotNone(self.user_1.user_profile)
        self.user_2 = get_user_model().objects.create_user(username='johndoe2',
                                                           password='illpassword',
                                                           email='johndoe2@example.com')
        self.user_2.is_staff= True
        self.user_2.save()
        self.assertIsNotNone(self.user_2.user_profile)
        self.user_3 = get_user_model().objects.create_user(username='johndoe3',
                                                           password='illpassword',
                                                           email='john3doe@example.com')
        self.assertIsNotNone(self.user_3.user_profile)
        self.user_4 = get_user_model().objects.create_user(username='inactive',
                                                           password='illpassword',
                                                           email='inactive@example.com')
        self.user_4.is_active = False
        self.user_4.save()
        self.assertIsNotNone(self.user_4.user_profile)
        self.user_no_profile = get_user_model().objects.create_user(username='no_profile',
                                                                    password='illpassword',
                                                                    email='no_profile@example.com')

    def test_accounts_list_view_available(self):
        """
        Test the availability of the "accounts list" view.
        """
        client = Client()
        response = client.get(reverse('accounts:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/accounts_list.html')
        self.assertIn('accounts', response.context)
        self.assertQuerysetEqual(response.context['accounts'], ['<UserProfile: Profile of "johndoe2">',
                                                                '<UserProfile: Profile of "johndoe1">',
                                                                '<UserProfile: Profile of "johndoe3">'])

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
        client.login(username='johndoe1', password='illpassword')
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
        client.login(username='johndoe1', password='illpassword')
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
        client.login(username='johndoe1', password='illpassword')
        response = client.get(reverse('myaccount:password_change_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_change_done.html')

    def test_public_user_account_view_available(self):
        """
        Test the availability of the "public user account" view.
        """
        client = Client()
        response = client.get(reverse('accounts:user_profile', kwargs={'username': 'johndoe1'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/public_user_account.html')
        self.assertIn('public_user', response.context)
        self.assertEqual(response.context['public_user'], self.user_1)
        self.assertIn('public_user_profile', response.context)
        self.assertEqual(response.context['public_user_profile'], self.user_1.user_profile)

    def test_public_user_account_view_available_no_profile(self):
        """
        Test the availability of the "public user account" view when the user has no profile in database yet.
        """
        client = Client()
        response = client.get(reverse('accounts:user_profile', kwargs={'username': 'no_profile'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/public_user_account.html')
        self.assertIn('public_user', response.context)
        self.assertEqual(response.context['public_user'], self.user_no_profile)
        self.assertIn('public_user_profile', response.context)
        self.assertEqual(response.context['public_user_profile'], self.user_no_profile.user_profile)

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
        client = Client()
        response = client.get(reverse('accounts:user_profile', kwargs={'username': 'inactive'}))
        self.assertEqual(response.status_code, 410)
        self.assertTemplateUsed(response, 'accounts/public_user_account.html')
