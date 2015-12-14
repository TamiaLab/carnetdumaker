"""
Tests suite for the views of the code snippets app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import CodeSnippet


class SnippetsViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        self.snippet = CodeSnippet.objects.create(title='Code 1',
                                                  author=author,
                                                  filename='helloworld.py',
                                                  description='Hello World written in Python 3',
                                                  source_code='print("Hello World!")\n')
        CodeSnippet.objects.create(title='Code 2',
                                   author=author,
                                   filename='helloworld.py',
                                   description='Hello World written in Python 3',
                                   source_code='print("Hello World!")\n')
        self.snippet_private = CodeSnippet.objects.create(title='Code 3',
                                                          author=author,
                                                          filename='helloworld.py',
                                                          description='Hello World written in Python 3',
                                                          source_code='print("Hello World!")\n',
                                                          public_listing=False)

    def test_snippet_list_view_available(self):
        """
        Test the availability of the "code snippet list" view.
        """
        client = Client()
        response = client.get(reverse('snippets:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'snippets/snippet_list.html')
        self.assertIn('snippets', response.context)
        self.assertQuerysetEqual(response.context['snippets'], ['<CodeSnippet: Code 2>',
                                                                '<CodeSnippet: Code 1>'])

    def test_snippet_detail_view_available(self):
        """
        Test the availability of the "code snippet detail" view.
        """
        client = Client()
        response = client.get(self.snippet.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'snippets/snippet_detail.html')
        self.assertIn('snippet', response.context)
        self.assertEqual(response.context['snippet'], self.snippet)

    def test_snippet_raw_view_available(self):
        """
        Test the availability of the "code snippet raw" view.
        """
        client = Client()
        response = client.get(self.snippet.get_raw_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.snippet.source_code, response.content.decode())
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Length'], str(len(self.snippet.source_code)))
        self.assertNotIn('Content-Disposition', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_snippet_download_view_available(self):
        """
        Test the availability of the "code snippet download" view.
        """
        client = Client()
        response = client.get(self.snippet.get_download_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.snippet.source_code, response.content.decode())
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Length'], str(len(self.snippet.source_code)))
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="%s"' % self.snippet.filename)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_private_snippet_detail_view_available(self):
        """
        Test the availability of the "code snippet detail" view for a private (not listed on index page) snippet.
        """
        client = Client()
        response = client.get(self.snippet_private.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'snippets/snippet_detail.html')
        self.assertIn('snippet', response.context)
        self.assertEqual(response.context['snippet'], self.snippet_private)

    def test_private_snippet_raw_view_available(self):
        """
        Test the availability of the "code snippet raw" view for a private (not listed on index page) snippet.
        """
        client = Client()
        response = client.get(self.snippet_private.get_raw_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.snippet_private.source_code, response.content.decode())
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Length'], str(len(self.snippet_private.source_code)))
        self.assertNotIn('Content-Disposition', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_private_snippet_download_view_available(self):
        """
        Test the availability of the "code snippet download" view for a private (not listed on index page) snippet.
        """
        client = Client()
        response = client.get(self.snippet_private.get_download_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.snippet_private.source_code, response.content.decode())
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Length'], str(len(self.snippet_private.source_code)))
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="%s"' % self.snippet_private.filename)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_snippet_detail_view_unavailable_with_unknown_snippet(self):
        """
        Test the unavailability of the "snippet detail" view with an unknown snippet ID.
        """
        client = Client()
        response = client.get(reverse('snippets:snippet_detail', kwargs={'pk': 1337}))
        self.assertEqual(response.status_code, 404)

    def test_latest_snippets_rss_feed_available(self):
        """
        Test the availability of the "latest snippets rss feed view.
        """
        client = Client()
        response = client.get(reverse('snippets:latest_snippets_rss'))
        self.assertEqual(response.status_code, 200)

    def test_latest_snippets_atom_feed_available(self):
        """
        Test the availability of the "latest snippets atom feed" view.
        """
        client = Client()
        response = client.get(reverse('snippets:latest_snippets_atom'))
        self.assertEqual(response.status_code, 200)
