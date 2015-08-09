"""
Tests suite for the models of the licenses app.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from ..models import License


class LicenseTestCase(TestCase):
    """
    Tests case for the ``License`` data model.
    """

    def _get_license(self):
        """
        Create a new license.
        :return: The newly created license.
        """
        license = License.objects.create(name='Test 1',
                                         slug='test-1',
                                         description='Hello World!')
        return license

    def test_default_values(self):
        """
        Test default values of newly created license.
        """
        license = self._get_license()
        self.assertEqual(None, license.logo)
        self.assertEqual('', license.usage)
        self.assertEqual('', license.source_url)
        self.assertIsNotNone(license.last_modification_date)

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        license = self._get_license()
        self.assertEqual(license.name, str(license))

    def test_get_absolute_url_method(self):
        """
        Test get_absolute_url method with a valid license.
        """
        license = self._get_license()
        excepted_url = reverse('licenses:license_detail', kwargs={'slug': license.slug})
        self.assertEqual(excepted_url, license.get_absolute_url())

    def test_ordering(self):
        """
        Test the ordering of license object.
        """
        License.objects.create(name='Test 1',
                               slug='test-1',
                               description='Hello World!')
        License.objects.create(name='Test 3',
                               slug='test-3',
                               description='Hello World!')
        License.objects.create(name='Test 2',
                               slug='test-2',
                               description='Hello World!')
        queryset = License.objects.all()
        self.assertQuerysetEqual(queryset, ['<License: Test 1>',
                                            '<License: Test 2>',
                                            '<License: Test 3>'])
