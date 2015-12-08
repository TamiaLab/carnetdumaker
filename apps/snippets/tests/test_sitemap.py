"""
Tests suite for the sitemap of the code snippets app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import CodeSnippet
from ..sitemap import CodeSnippetsSitemap


class CodeSnippetSitemapTestCase(TestCase):
    """
    Tests suite for the ``CodeSnippetSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        CodeSnippet.objects.create(title='Code 1',
                                   author=author,
                                   filename='helloworld.py',
                                   description='Hello World written in Python 3',
                                   source_code='print("Hello World!")\n')
        CodeSnippet.objects.create(title='Code 2',
                                   author=author,
                                   filename='helloworld.py',
                                   description='Hello World written in Python 3',
                                   source_code='print("Hello World!")\n')
        CodeSnippet.objects.create(title='Code 3',
                                   author=author,
                                   filename='helloworld.py',
                                   description='Hello World written in Python 3',
                                   source_code='print("Hello World!")\n')

        # Test the resulting sitemap content
        sitemap = CodeSnippetsSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<CodeSnippet: Code 3>',
                                         '<CodeSnippet: Code 2>',
                                         '<CodeSnippet: Code 1>'])

    def test_lastmod(self):
        """
        Test the ``lastmod`` method of the sitemap with an announcement modified after being published.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')
        snippet.title = 'Code 1 - reborn'
        snippet.save()
        self.assertIsNotNone(snippet.last_modification_date)
        self.assertIsNotNone(snippet.creation_date)

        # Test the result of the method
        sitemap = CodeSnippetsSitemap()
        self.assertEqual(sitemap.lastmod(snippet), snippet.last_modification_date)

    def test_lastmod_no_modification(self):
        """
        Test the ``lastmod`` method of the sitemap with an announcement never modified.
        """

        # Create some test fixtures
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Code 1',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')
        self.assertIsNone(snippet.last_modification_date)
        self.assertIsNotNone(snippet.creation_date)

        # Test the result of the method
        sitemap = CodeSnippetsSitemap()
        self.assertEqual(sitemap.lastmod(snippet), snippet.creation_date)
