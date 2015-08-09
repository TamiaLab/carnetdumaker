"""
Tests suite for the force-logout app.
"""

from unittest import mock
from datetime import timedelta

from django.utils import timezone
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import (ForceLogoutOrder,
                      FORCE_LOGOUT_SESSION_KEY)


class ForceLogoutOrderTestCase(TestCase):
    """
    Tests suite for the ``ForceLogoutOrder`` data model.
    """

    def test_str_method(self):
        """
        Test the result of the ``__str__`` method.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        order = ForceLogoutOrder(user=user)
        self.assertEqual('Logout order for "%s"' % order.user.username, str(order))

    def test_ordering(self):
        """
        Test the ordering of logout order.
        """
        user1 = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        ForceLogoutOrder.objects.force_logout(user1)
        user2 = get_user_model().objects.create_user(username='johnsmith',
                                                    password='illpassword',
                                                    email='john.smith@example.com')
        ForceLogoutOrder.objects.force_logout(user2)

        queryset = ForceLogoutOrder.objects.all()
        self.assertQuerysetEqual(queryset, ['<ForceLogoutOrder: Logout order for "johnsmith">',
                                            '<ForceLogoutOrder: Logout order for "johndoe">'])

    def test_force_logout(self):
        """
        Test the ``force_logout`` manager method.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')
        self.assertEqual(ForceLogoutOrder.objects.count(), 0)

        now = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            order = ForceLogoutOrder.objects.force_logout(user)
            self.assertEqual(order.user, user)
            self.assertEqual(order.order_date, now)
        self.assertEqual(ForceLogoutOrder.objects.count(), 1)

        # Test update
        future_now = now + timedelta(seconds=10)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = future_now
            order = ForceLogoutOrder.objects.force_logout(user)
            self.assertEqual(order.user, user)
            self.assertEqual(order.order_date, future_now)
        self.assertEqual(ForceLogoutOrder.objects.count(), 1)

    def test_store_current_session_login_timestamp(self):
        """
        Test the current session login timestamp persistence.
        """
        get_user_model().objects.create_user(username='johndoe',
                                             password='illpassword',
                                             email='john.doe@example.com')
        now = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            c = Client()
            c.login(username='johndoe', password='illpassword')

        # Persistence tests
        self.assertIn(FORCE_LOGOUT_SESSION_KEY, c.session)
        self.assertEqual(now.timestamp(), c.session[FORCE_LOGOUT_SESSION_KEY])
