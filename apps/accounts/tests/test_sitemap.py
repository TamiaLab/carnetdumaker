"""
Tests suite for the sitemap of the user accounts app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..sitemap import AccountsSitemap


class AccountsSitemapTestCase(TestCase):
    """
    Tests case for the ``AccountsSitemap`` class.
    """

    def test_sitemap_generation(self):
        """
        Test the queryset result of the sitemap.
        """

        # Create some test users.
        j1 = get_user_model().objects.create_user(username='johndoe',
                                                  password='illpassword',
                                                  email='john.doe@example.com')
        j2 = get_user_model().objects.create_user(username='johndoe2',
                                                  password='illpassword',
                                                  email='john.doe@example.com')
        j3 = get_user_model().objects.create_user(username='johndoe3',
                                                  password='illpassword',
                                                  email='john.doe@example.com')
        j3.is_active = False
        j3.save()

        # Init user accounts
        self.assertIsNotNone(j1)
        self.assertIsNotNone(j1.user_profile)
        self.assertIsNotNone(j2)
        self.assertIsNotNone(j2.user_profile)
        self.assertIsNotNone(j3)
        self.assertIsNotNone(j3.user_profile)

        # Test the resulting sitemap content
        sitemap = AccountsSitemap()
        items = sitemap.items()
        self.assertEqual(len(items), 2)
        self.assertIn(j1.user_profile, items)
        self.assertIn(j2.user_profile, items)
        self.assertNotIn(j3.user_profile, items)

    def test_sitemap_location(self):
        """
        Test the ``location`` result of the sitemap.
        """
        j1 = get_user_model().objects.create_user(username='johndoe',
                                                  password='illpassword',
                                                  email='john.doe@example.com')
        self.assertIsNotNone(j1)
        self.assertIsNotNone(j1.user_profile)

        sitemap = AccountsSitemap()
        result = sitemap.location(j1.user_profile)
        self.assertEqual(j1.user_profile.get_absolute_url(), result)

    def test_sitemap_lastmod(self):
        """
        Test the ``lastmod`` result of the sitemap.
        """
        j1 = get_user_model().objects.create_user(username='johndoe',
                                                  password='illpassword',
                                                  email='john.doe@example.com')
        self.assertIsNotNone(j1)
        self.assertIsNotNone(j1.user_profile)

        sitemap = AccountsSitemap()
        result = sitemap.lastmod(j1.user_profile)
        self.assertEqual(j1.user_profile.last_modification_date, result)
