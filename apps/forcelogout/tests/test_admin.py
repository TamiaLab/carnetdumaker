"""
Tests suite for the admin views of the force-logout app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import ForceLogoutOrder


class ForceLogoutOrderAdminViewsTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        author = get_user_model().objects.create_superuser(username='johndoe',
                                                           password='illpassword',
                                                           email='john.doe@example.com')
        self.order = ForceLogoutOrder.objects.create(user=author,
                                                     order_date=timezone.now())

    def test_order_list_view_available(self):
        """
        Test the availability of the "logout order list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:forcelogout_forcelogoutorder_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_order_edit_view_available(self):
        """
        Test the availability of the "edit logout order" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:forcelogout_forcelogoutorder_change', args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)
