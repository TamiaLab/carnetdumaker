"""
Tests suite for the multi-upload form field app.
"""

from django import forms
from django.test import SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict

from .fields import MultiFileField


class TestForm(forms.Form):
    """
    Simple test form class.
    """

    files = MultiFileField()


class TestFormWithMinNum(forms.Form):
    """
    Simple test form class with min_num=2 set.
    """

    files = MultiFileField(min_num=2)


class TestFormWithMaxNum(forms.Form):
    """
    Simple test form class with max_num=2 set.
    """

    files = MultiFileField(max_num=2)


class TestFormWithMaxFileSize(forms.Form):
    """
    Simple test form class with max_file_size=512 set.
    """

    files = MultiFileField(max_file_size=512)


class TestFormWithMaxTotalFileSize(forms.Form):
    """
    Simple test form class with max_total_file_size=1024 set.
    """

    files = MultiFileField(max_total_file_size=1024)


class MultiFileFieldTestCase(SimpleTestCase):
    """
    Tests suite for the multi-upload form field.
    """

    def test_form_instance(self):
        """
        Test if the form with the field can be instantiated without error.
        """
        form = TestForm()
        self.assertIsNotNone(form)
        form = TestFormWithMinNum()
        self.assertIsNotNone(form)
        form = TestFormWithMaxNum()
        self.assertIsNotNone(form)
        form = TestFormWithMaxFileSize()
        self.assertIsNotNone(form)
        form = TestFormWithMaxTotalFileSize()
        self.assertIsNotNone(form)

    def test_files_field(self):
        """
        Test if the field works with some files.
        """
        post = {}
        files_ = [
            SimpleUploadedFile('test1.txt', b'A' * 512),
            SimpleUploadedFile('test2.txt', b'A' * 512)
        ]
        files = MultiValueDict({
            'files': files_
        })
        form = TestForm(post, files)
        self.assertTrue(form.is_valid())
        self.assertEqual(form['files'].value(), files_)

    def test_min_num_constrain(self):
        """
        Test if the field throws validation error if the min_num constrain is not reached.
        """
        post = {}
        files = MultiValueDict({
            'files': [
                SimpleUploadedFile('test1.txt', b'A' * 512)
            ]
        })
        form = TestFormWithMinNum(post, files)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('files', errors)
        self.assertEqual(len(errors['files']), 1)
        self.assertEqual(errors['files'][0].code, 'min_num')

    def test_min_num_constrain_just(self):
        """
        Test if the field throws validation error if the min_num constrain is just reached.
        """
        post = {}
        files_ = [
            SimpleUploadedFile('test1.txt', b'A' * 512),
            SimpleUploadedFile('test1.txt', b'A' * 512)
        ]
        files = MultiValueDict({
            'files': files_
        })
        form = TestFormWithMinNum(post, files)
        self.assertTrue(form.is_valid())
        self.assertEqual(form['files'].value(), files_)

    def test_max_num_constrain(self):
        """
        Test if the field throws validation error if the max_num constrain is reached.
        """
        post = {}
        files = MultiValueDict({
            'files': [
                SimpleUploadedFile('test1.txt', b'A' * 512),
                SimpleUploadedFile('test2.txt', b'A' * 512),
                SimpleUploadedFile('test3.txt', b'A' * 512),
            ]
        })
        form = TestFormWithMaxNum(post, files)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('files', errors)
        self.assertEqual(len(errors['files']), 1)
        self.assertEqual(errors['files'][0].code, 'max_num')

    def test_max_num_constrain_just(self):
        """
        Test if the field throws validation error if the max_num constrain is just reached.
        """
        post = {}
        files_ = [
            SimpleUploadedFile('test1.txt', b'A' * 512),
            SimpleUploadedFile('test2.txt', b'A' * 512)
        ]
        files = MultiValueDict({
            'files': files_
        })
        form = TestFormWithMaxNum(post, files)
        self.assertTrue(form.is_valid())
        self.assertEqual(form['files'].value(), files_)

    def test_max_file_size_constrain(self):
        """
        Test if the field throws validation error if the max_file_size constrain is reached.
        """
        post = {}
        files = MultiValueDict({
            'files': [
                SimpleUploadedFile('test1.txt', b'A' * 513),
            ]
        })
        form = TestFormWithMaxFileSize(post, files)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('files', errors)
        self.assertEqual(len(errors['files']), 1)
        self.assertEqual(errors['files'][0].code, 'max_file_size')

    def test_max_file_size_constrain_just(self):
        """
        Test if the field throws validation error if the max_file_size constrain is just reached.
        """
        post = {}
        files_ = [
            SimpleUploadedFile('test1.txt', b'A' * 512),
        ]
        files = MultiValueDict({
            'files': files_
        })
        form = TestFormWithMaxFileSize(post, files)
        self.assertTrue(form.is_valid())
        self.assertEqual(form['files'].value(), files_)

    def test_max_total_file_size_constrain(self):
        """
        Test if the field throws validation error if the max_total_file_size constrain is reached.
        """
        post = {}
        files = MultiValueDict({
            'files': [
                SimpleUploadedFile('test1.txt', b'A' * 512),
                SimpleUploadedFile('test2.txt', b'A' * 513)
            ]
        })
        form = TestFormWithMaxTotalFileSize(post, files)
        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('files', errors)
        self.assertEqual(len(errors['files']), 1)
        self.assertEqual(errors['files'][0].code, 'max_total_file_size')

    def test_max_total_file_size_constrain_just(self):
        """
        Test if the field throws validation error if the max_total_file_size constrain is just reached.
        """
        post = {}
        files_ = [
            SimpleUploadedFile('test1.txt', b'A' * 512),
            SimpleUploadedFile('test2.txt', b'A' * 512),
        ]
        files = MultiValueDict({
            'files': files_
        })
        form = TestFormWithMaxTotalFileSize(post, files)
        self.assertTrue(form.is_valid())
        self.assertEqual(form['files'].value(), files_)
