"""
Tests suite for the data models of the code snippet app.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import CodeSnippet
from ..constants import CODE_LANGUAGE_DEFAULT
from ..settings import (SNIPPETS_DEFAULT_TABULATION_SIZE,
                        SNIPPETS_DISPLAY_LINE_NUMBERS_BY_DEFAULT)


class CodeSnippetModelTestCase(TestCase):
    """
    Tests suite for the ``CodeSnippet`` data model class.
    """

    def _get_snippet(self):
        """
        Creates and returns a new code snippet.
        :return: The newly created snippet.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        snippet = CodeSnippet.objects.create(title='Python Hello World',
                                             author=author,
                                             filename='helloworld.py',
                                             description='Hello World written in Python 3',
                                             source_code='print("Hello World!")\n')
        return snippet

    def test_default_values(self):
        """
        Test defaults value of a newly created snippet.
        """
        snippet = self._get_snippet()
        self.assertEqual(CODE_LANGUAGE_DEFAULT, snippet.code_language)
        self.assertTrue(snippet.public_listing)
        self.assertIsNone(snippet.license)
        self.assertNotEqual('', snippet.html_for_display)
        self.assertNotEqual('', snippet.css_for_display)
        self.assertEqual(snippet.display_line_numbers, SNIPPETS_DISPLAY_LINE_NUMBERS_BY_DEFAULT)
        self.assertEqual('', snippet.highlight_lines)
        self.assertEqual(snippet.tab_size, SNIPPETS_DEFAULT_TABULATION_SIZE)
        self.assertIsNotNone(snippet.creation_date)
        self.assertIsNone(snippet.last_modification_date)

    def test_str_method(self):
        """
        Test the ``__str__`` method of the model for other tests.
        """
        snippet = self._get_snippet()
        self.assertEqual(snippet.title, str(snippet))

    def test_get_absolute_url_method(self):
        """
        Test the ``get_absolute_url`` method of the model.
        """
        snippet = self._get_snippet()
        excepted_url = reverse('snippets:snippet_detail', kwargs={'pk': snippet.pk})
        self.assertEqual(excepted_url, snippet.get_absolute_url())

    def test_get_raw_url_method(self):
        """
        Test the ``get_raw_url`` method of the model.
        """
        snippet = self._get_snippet()
        excepted_url = reverse('snippets:snippet_raw', kwargs={'pk': snippet.pk})
        self.assertEqual(excepted_url, snippet.get_raw_url())

    def test_get_download_url_method(self):
        """
        Test the ``get_download_url`` method of the model.
        """
        snippet = self._get_snippet()
        excepted_url = reverse('snippets:snippet_download', kwargs={'pk': snippet.pk})
        self.assertEqual(excepted_url, snippet.get_download_url())

    def test_get_zip_download_url_method(self):
        """
        Test the ``get_zip_download_url`` method of the model.
        """
        snippet = self._get_snippet()
        excepted_url = reverse('snippets:snippet_zip_download', kwargs={'pk': snippet.pk})
        self.assertEqual(excepted_url, snippet.get_zip_download_url())

    def test_last_modification_date_change_after_title_change(self):
        """
        Test if the ``last_modification_date`` change after the title is modified.
        """
        snippet = self._get_snippet()
        before_date = snippet.last_modification_date
        self.assertIsNone(before_date)
        snippet.title = 'New title'
        snippet.save()
        after_date = snippet.last_modification_date
        self.assertIsNotNone(after_date)
        self.assertNotEqual(after_date, before_date)

    def test_last_modification_date_change_after_filename_change(self):
        """
        Test if the ``last_modification_date`` change after the filename is modified.
        """
        snippet = self._get_snippet()
        before_date = snippet.last_modification_date
        self.assertIsNone(before_date)
        snippet.filename = 'new_filename.py'
        snippet.save()
        after_date = snippet.last_modification_date
        self.assertIsNotNone(after_date)
        self.assertNotEqual(after_date, before_date)

    def test_last_modification_date_change_after_description_change(self):
        """
        Test if the ``last_modification_date`` change after the description is modified.
        """
        snippet = self._get_snippet()
        before_date = snippet.last_modification_date
        self.assertIsNone(before_date)
        snippet.description = 'New description'
        snippet.save()
        after_date = snippet.last_modification_date
        self.assertIsNotNone(after_date)
        self.assertNotEqual(after_date, before_date)

    def test_last_modification_date_change_after_source_code_change(self):
        """
        Test if the ``last_modification_date`` change after the source code is modified.
        """
        snippet = self._get_snippet()
        before_date = snippet.last_modification_date
        self.assertIsNone(before_date)
        snippet.source_code = 'print("New source code");'
        snippet.save()
        after_date = snippet.last_modification_date
        self.assertIsNotNone(after_date)
        self.assertNotEqual(after_date, before_date)

    def test_last_modification_date_not_change_after_other_change(self):
        """
        Test if the ``last_modification_date`` change after any other fields is modified.
        """
        new_author = get_user_model().objects.create_user(username='johnsmith',
                                                          password='illpassword',
                                                          email='john.smith@example.com')
        snippet = self._get_snippet()
        self.assertIsNone(snippet.last_modification_date)
        snippet.author = new_author
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.code_language = 'yaml'
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.public_listing = False
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.html_for_display = 'HTMLLLLL'
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.css_for_display = 'CSSSSSSS'
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.display_line_numbers = True
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.display_line_numbers = False
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.highlight_lines = '1,2'
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)
        snippet.tab_size = 8
        snippet.save()
        self.assertIsNone(snippet.last_modification_date)

    def test_has_been_modified_last_mod_date_null(self):
        """
        Test if the ``has_been_modified`` method return False when the snippet was never modified.
        """
        snippet = self._get_snippet()
        self.assertIsNone(snippet.last_modification_date)
        self.assertFalse(snippet.has_been_modified())

    def test_has_been_modified_after_modification(self):
        """
        Test if the ``has_been_modified`` method return True when the snippet is modified.
        """
        snippet = self._get_snippet()
        self.assertIsNone(snippet.last_modification_date)
        snippet.title = 'New title'
        snippet.save()
        self.assertIsNotNone(snippet.last_modification_date)
        self.assertTrue(snippet.has_been_modified())

    def test_save_do_highlighting(self):
        """
        Test if saving the snippet do the highlighting.
        """
        snippet = self._get_snippet()
        self.assertNotEqual('', snippet.html_for_display)
        self.assertNotEqual('', snippet.css_for_display)

    def test_get_highlight_lines_with_no_input(self):
        """
        Test if the ``get_highlight_lines`` of the model return an empty string with an empty string as input.
        """
        snippet = self._get_snippet()
        snippet.highlight_lines = ''
        self.assertEqual([], snippet.get_highlight_lines())

    def test_get_highlight_lines_with_numbers(self):
        """
        Test if the ``get_highlight_lines`` of the model return a list of int with a comma separated list of str(int).
        """
        snippet = self._get_snippet()
        snippet.highlight_lines = '1,2,3'
        self.assertEqual([1, 2, 3], snippet.get_highlight_lines())

    def test_public_snippets(self):
        """
        Test the result of ``public_snippets`` method of the objects manager.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        snippet_public = CodeSnippet.objects.create(title='Python Hello World',
                                                    author=author,
                                                    filename='helloworld.py',
                                                    description='Hello World written in Python 3',
                                                    source_code='print("Hello World!")\n')
        snippet_private = CodeSnippet.objects.create(title='Python Hello World',
                                                     author=author,
                                                     filename='helloworld.py',
                                                     description='Hello World written in Python 3',
                                                     source_code='print("Hello World!")\n',
                                                     public_listing=False)

        # Test the method
        queryset_public = CodeSnippet.objects.public_snippets()
        self.assertEqual(len(queryset_public), 1)
        self.assertIn(snippet_public, queryset_public)
        self.assertNotIn(snippet_private, queryset_public)

    def test_snippets_ordering(self):
        """
        Test the default ordering of the snippets.
        """
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

        # Test the ordering
        queryset_public = CodeSnippet.objects.public_snippets()
        self.assertQuerysetEqual(queryset_public, ['<CodeSnippet: Code 3>',
                                                   '<CodeSnippet: Code 2>',
                                                   '<CodeSnippet: Code 1>'])
