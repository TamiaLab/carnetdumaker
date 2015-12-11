"""
Tests suite for the forms of the change email app.
"""

from django.test import SimpleTestCase

from ..forms import EmailChangeForm


class EmailChangeFormTestCase(SimpleTestCase):
    """
    Tests case for the ``EmailChangeForm`` class.
    """

    def test_fields_presents(self):
        """
        Really simple test to check if the two email fields are presents.
        """
        form = EmailChangeForm()
        self.assertIn('new_email1', form.fields)
        self.assertIn('new_email2', form.fields)

    def test_fields_mismatch(self):
        """
        Test if the form detect erroneously-copied email.
        """
        post = {
            'new_email1': 'foo@example.com',
            'new_email2': 'bar@example.com',
        }
        form = EmailChangeForm(post)
        self.assertFalse(form.is_valid())

        errors = form.errors.as_data()
        self.assertEqual(len(errors), 1)
        self.assertIn('new_email2', errors)
        self.assertEqual(len(errors['new_email2']), 1)
        self.assertEqual(errors['new_email2'][0].code, 'email_mismatch')
