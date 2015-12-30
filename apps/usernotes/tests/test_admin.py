"""
Tests suite for the admin views of the user notes app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import UserNote


class UserNoteAdminTestCase(TestCase):
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
        self.note = UserNote.objects.create(title='Test note',
                                            author=self.author,
                                            description='Test note description',
                                            target_user=self.user)

    def test_note_list_view_available(self):
        """
        Test the availability of the "user note list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:usernotes_usernote_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_note_edit_view_available(self):
        """
        Test the availability of the "edit user note" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:usernotes_usernote_change', args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
