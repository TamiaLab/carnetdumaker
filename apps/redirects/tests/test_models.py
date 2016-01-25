"""
Tests suite for the data models of the redirect app.
"""
from django.test import TestCase
from django.conf import settings

from ..models import Redirection


class RedirectionModelTestCase(TestCase):
    """
    Tests suite for the ``Redirection`` data model class.
    """

    def _get_redirection(self):
        """
        Creates and returns a new redirection.
        :return: The newly created redirection.
        """
        redirection = Redirection.objects.create(site_id=settings.SITE_ID,
                                                 old_path='/404/')
        return redirection

    def test_default_values(self):
        """
        Test defaults value of a newly created redirection.
        """
        redirection = self._get_redirection()
        self.assertEqual(settings.SITE_ID, redirection.site_id)
        self.assertEqual('/404/', redirection.old_path)
        self.assertEqual('', redirection.new_path)
        self.assertTrue(redirection.permanent_redirect)
        self.assertTrue(redirection.active)

    def test_str_method(self):
        """
        Test the ``__str__`` method of the model for other tests.
        """
        redirection = self._get_redirection()
        self.assertEqual("[%s] %s -> %s" % (redirection.site.domain,
                                            redirection.old_path, redirection.new_path), str(redirection))
