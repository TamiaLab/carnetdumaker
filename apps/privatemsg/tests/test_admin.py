"""
Tests suite for the admin views of the private messages app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import PrivateMessage, BlockedUser


class PrivateMessageAdminTestCase(TestCase):
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
        self.msg = PrivateMessage.objects.create(sender=self.author,
                                                 recipient=self.author,
                                                 subject='Test',
                                                 body='Test')

    def test_private_message_list_view_available(self):
        """
        Test the availability of the "private message list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:privatemsg_privatemessage_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_private_message_edit_view_available(self):
        """
        Test the availability of the "edit private message" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:privatemsg_privatemessage_change', args=[self.msg.pk]))
        self.assertEqual(response.status_code, 200)


class PrivateMessageUserProfileAdminTestCase(TestCase):
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
        self.privatemsg_profile = self.author.privatemsg_profile

    def test_private_message_profile_list_view_available(self):
        """
        Test the availability of the "private messages profile list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:privatemsg_privatemessageuserprofile_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_private_message_profile_edit_view_available(self):
        """
        Test the availability of the "edit private messages profile" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:privatemsg_privatemessageuserprofile_change',
                                      args=[self.privatemsg_profile.pk]))
        self.assertEqual(response.status_code, 200)


class BlockedUserAdminTestCase(TestCase):
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
        self.blocked_user = BlockedUser.objects.create(user=self.author,
                                                       blocked_user=self.author)

    def test_blocked_user_list_view_available(self):
        """
        Test the availability of the "blocked user list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:privatemsg_blockeduser_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_blocked_user_edit_view_available(self):
        """
        Test the availability of the "edit blocked user" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:privatemsg_blockeduser_change',
                                      args=[self.blocked_user.pk]))
        self.assertEqual(response.status_code, 200)
