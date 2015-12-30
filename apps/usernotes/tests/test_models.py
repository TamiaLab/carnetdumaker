"""
Tests suite for the data models of the user notes app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import UserNote


class UserNoteModelTestCase(TestCase):
    """
    Tests suite for the ``UserNote`` data model class.
    """

    def _get_note(self):
        """
        Creates some test fixtures.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        user = get_user_model().objects.create_user(username='johnsmith',
                                                      password='illpassword',
                                                      email='john.smith@example.com')
        note = UserNote.objects.create(title='Test note',
                                       author=author,
                                       description='Test note description',
                                       target_user=user)
        return note, author, user

    def test_default_values(self):
        """
        Test defaults value of a newly created note.
        """
        note, author, user = self._get_note()
        self.assertIsNotNone(note.creation_date)
        self.assertIsNotNone(note.last_modification_date)
        self.assertFalse(note.sticky)

    def test_str_method(self):
        """
        Test the ``__str__`` method of the model for other tests.
        """
        note, author, user = self._get_note()
        self.assertEqual(note.title, str(note))
