"""
Tests suite for the forms of the user API key app.
"""

from django.test import SimpleTestCase

from ..forms import KeyRegenerationConfirmationForm


class KeyRegenerationConfirmationFormTestCase(SimpleTestCase):
    """
    Tests case for the ``KeyRegenerationConfirmationForm`` class.
    """

    def test_fields_presents(self):
        """
        Really simple test to check if the confirmation field is present.
        """
        form = KeyRegenerationConfirmationForm()
        self.assertIn('confirm', form.fields)
        self.assertFalse(form.fields['confirm'].initial)

    def test_fields_required(self):
        """
        Test if the form fail when confirmation is not given.
        """
        post = {
            'confirm': '',
        }
        form = KeyRegenerationConfirmationForm(post)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('confirm', errors)
        self.assertEqual(len(errors['confirm']), 1)
        self.assertEqual(errors['confirm'][0].code, 'required')

    def test_fields_good(self):
        """
        Test if the form success when confirmation is given.
        """
        post = {
            'confirm': '1',
        }
        form = KeyRegenerationConfirmationForm(post)
        self.assertTrue(form.is_valid())
