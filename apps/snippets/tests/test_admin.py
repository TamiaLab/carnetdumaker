"""
Tests suite for the admin views of the code snippets app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import CodeSnippet


class CodeSnippetAdminTestCase(TestCase):
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
        self.snippet = CodeSnippet.objects.create(title='Python Hello World',
                                                  author=self.author,
                                                  filename='helloworld.py',
                                                  description='Hello World written in Python 3',
                                                  source_code='print("Hello World!")\n')

    def test_snippet_list_view_available(self):
        """
        Test the availability of the "code snippet list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:snippets_codesnippet_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_snippet_edit_view_available(self):
        """
        Test the availability of the "edit code snippet" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:snippets_codesnippet_change', args=[self.snippet.pk]))
        self.assertEqual(response.status_code, 200)
