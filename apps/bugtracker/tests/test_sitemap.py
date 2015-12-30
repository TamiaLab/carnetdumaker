"""
Tests suite for the sitemap of the bug tracker app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import IssueTicket
from ..sitemap import IssueTicketsSitemap


class IssueTicketsSitemapTestCase(TestCase):
    """
    Tests suite for the ``IssueTicketsSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        IssueTicket.objects.create(title='Test ticket 1',
                                   description='Test',
                                   submitter=user,
                                   assigned_to=user)
        IssueTicket.objects.create(title='Test ticket 2',
                                   description='Test',
                                   submitter=user,
                                   assigned_to=user)

        # Test the resulting sitemap content
        sitemap = IssueTicketsSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<IssueTicket: Test ticket 2>',
                                         '<IssueTicket: Test ticket 1>'])

    def test_lastmod(self):
        """
        Test the ``lastmod`` method of the sitemap with an article modified after being published.
        """

        # Create some test fixtures
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ticket = IssueTicket.objects.create(title='Test ticket 1',
                                            description='Test',
                                            submitter=user,
                                            assigned_to=user)

        # Test the result of the method
        sitemap = IssueTicketsSitemap()
        self.assertEqual(sitemap.lastmod(ticket), ticket.last_modification_date)
