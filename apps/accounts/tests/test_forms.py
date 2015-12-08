"""
Tests suite for the forms of the user accounts app.
"""

from io import BytesIO

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile

from ..forms import UserProfileModificationForm
from ..settings import (AVATAR_HEIGHT_SIZE_PX,
                        AVATAR_WIDTH_SIZE_PX,
                        AVATAR_HEIGHT_SIZE_PX_MAX,
                        AVATAR_WIDTH_SIZE_PX_MAX)


class UserProfileModificationFormTestCase(TestCase):
    """
    Tests case for the ``UserProfileModificationForm`` edition form.
    """

    def setUp(self):
        """
        Create a dummy user for the tests.
        """
        self.user = get_user_model().objects.create_user(username='dummy',
                                                         password='illpassword',
                                                         email='dummy@example.com')
        self.user_profile = self.user.user_profile

    def _generate_dummy_image(self, height, width):
        """
        Generate a dummy image (blank).
        :param height: The desired height of the image.
        :param width: The desired width of the image.
        :return: The image as an ``InMemoryUploadedFile`` file-like object.
        """
        data = BytesIO()
        image = Image.new("RGB", (width, height), "black")
        image.save(data, format='JPEG')
        data.seek(0)
        return InMemoryUploadedFile(data, None, 'foobar.jpg', 'image/jpeg', len(data.getvalue()), None)

    def test_first_and_last_name_as_initial(self):
        """
        Test if the form constructor set correctly the initial value of the first and last name fields.
        """
        form = UserProfileModificationForm(instance=self.user_profile)
        self.assertEqual(self.user.first_name, form.fields['first_name'].initial)
        self.assertEqual(self.user.last_name, form.fields['last_name'].initial)

    def test_save_first_and_last_names_with_profile(self):
        """
        Test if the form save the first and last names, along with the user profile data.
        """
        post = {
            'timezone': 'Europe/Paris',
            'preferred_language': 'fr',
            'country': 'FRA',

            'first_name': 'test',
            'last_name': 'test2',
            'location': 'here',
        }
        form = UserProfileModificationForm(post, instance=self.user_profile)
        self.assertTrue(form.is_valid())
        res = form.save()
        self.assertEqual(res, self.user_profile)
        self.assertEqual('here', self.user_profile.location)
        self.assertEqual('test', self.user.first_name)
        self.assertEqual('test2', self.user.last_name)

    def test_no_avatar(self):
        """
        Test if the form work when no avatar is uploaded.
        """
        post = {
            'timezone': 'Europe/Paris',
            'preferred_language': 'fr',
            'country': 'FRA',
        }
        form = UserProfileModificationForm(post, instance=self.user_profile)
        self.assertTrue(form.is_valid())

    def test_avatar_height_too_big(self):
        """
        Test if the form show an error when the uploaded avatar height is too big.
        """
        files = {
            'avatar': self._generate_dummy_image(AVATAR_HEIGHT_SIZE_PX, AVATAR_WIDTH_SIZE_PX_MAX + 1)
        }
        post = {
            'timezone': 'Europe/Paris',
            'preferred_language': 'fr',
            'country': 'FRA',
        }
        form = UserProfileModificationForm(post, files, instance=self.user_profile)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('avatar', errors)
        self.assertEqual(len(errors['avatar']), 1)
        self.assertEqual(errors['avatar'][0].code, 'avatar_toobig')

    def test_avatar_height_too_small(self):
        """
        Test if the form show an error when the uploaded avatar height is too small.
        """
        files = {
            'avatar': self._generate_dummy_image(AVATAR_HEIGHT_SIZE_PX, AVATAR_WIDTH_SIZE_PX - 1)
        }
        post = {
            'timezone': 'Europe/Paris',
            'preferred_language': 'fr',
            'country': 'FRA',
        }
        form = UserProfileModificationForm(post, files, instance=self.user_profile)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('avatar', errors)
        self.assertEqual(len(errors['avatar']), 1)
        self.assertEqual(errors['avatar'][0].code, 'avatar_toosmall')

    def test_avatar_width_too_big(self):
        """
        Test if the form show an error when the uploaded avatar width is too big.
        """
        files = {
            'avatar': self._generate_dummy_image(AVATAR_HEIGHT_SIZE_PX_MAX + 1, AVATAR_WIDTH_SIZE_PX)
        }
        post = {
            'timezone': 'Europe/Paris',
            'preferred_language': 'fr',
            'country': 'FRA',
        }
        form = UserProfileModificationForm(post, files, instance=self.user_profile)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('avatar', errors)
        self.assertEqual(len(errors['avatar']), 1)
        self.assertEqual(errors['avatar'][0].code, 'avatar_toobig')

    def test_avatar_width_too_small(self):
        """
        Test if the form show an error when the uploaded avatar width is too small.
        """
        files = {
            'avatar': self._generate_dummy_image(AVATAR_HEIGHT_SIZE_PX - 1, AVATAR_WIDTH_SIZE_PX)
        }
        post = {
            'timezone': 'Europe/Paris',
            'preferred_language': 'fr',
            'country': 'FRA',
        }
        form = UserProfileModificationForm(post, files, instance=self.user_profile)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('avatar', errors)
        self.assertEqual(len(errors['avatar']), 1)
        self.assertEqual(errors['avatar'][0].code, 'avatar_toosmall')
