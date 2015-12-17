"""
Tests suite for the views of the text rendering app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as _


class TextRenderingViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        get_user_model().objects.create_user(username='johndoe',
                                             password='illpassword',
                                             email='john.doe@example.com')

    def test_preview_rendering(self):
        """
        Test the ``preview_rendering`` view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.post(reverse('txtrender:preview'), {'content': '[b]Hello World![/b]'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('output_html', response.context)
        self.assertEqual(response.context['output_html'], '<p class="text-justify"><strong>Hello World!</strong></p>\n')

    def test_preview_rendering_not_post(self):
        """
        Test the ``preview_rendering`` view with GET (not POST).
        """
        client = Client()
        response = client.get(reverse('txtrender:preview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, force_bytes(_('This view only handle POST requests!')))

    def test_preview_rendering_not_authenticated(self):
        """
        Test the ``preview_rendering`` view with anonymous user.
        """
        client = Client()
        response = client.post(reverse('txtrender:preview'), {'content': '[b]Hello World![/b]'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, force_bytes(_("Beware! You are not logged-in!")))

    def test_preview_rendering_no_input(self):
        """
        Test the ``preview_rendering`` view with no input.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.post(reverse('txtrender:preview'), {'content': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
