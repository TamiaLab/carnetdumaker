"""
Test suite for the force-logout app.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import (ForceLogoutOrder,
                      FORCE_LOGOUT_SESSION_KEY)


class ForceLogoutMiddlewareTestCase(TestCase):
    """
    Test suite for the ``ForceLogoutMiddleware``.
    """

    def test_middleware_installed(self):
        """
        Test if the ``ForceLogoutMiddleware`` is installed.
        """
        from django.conf import settings
        self.assertIn('apps.forcelogout.middleware.ForceLogoutMiddleware', settings.MIDDLEWARE_CLASSES)

    def test_anonymous_user(self):
        """
        Test if the ``ForceLogoutMiddleware`` work as excepted when the current user is not authenticated.
        """
        c = Client()
        response = c.get('/')
        self.assertFalse(response.context["user"].is_authenticated())

    def test_force_logout_middleware_without_order(self):
        """
        Test if the ``ForceLogoutMiddleware`` work as excepted when no logout order is made.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')

        with self.assertRaises(ForceLogoutOrder.DoesNotExist):
            ForceLogoutOrder.objects.get(user=user)

        c = Client()
        c.login(username='johndoe', password='illpassword')
        response = c.get('/')
        self.assertTrue(response.context["user"].is_authenticated())

    def test_force_logout_middleware_with_order(self):
        """
        Test if the ``ForceLogoutMiddleware`` work as excepted when a logout order is made.
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')

        with self.assertRaises(ForceLogoutOrder.DoesNotExist):
            ForceLogoutOrder.objects.get(user=user)

        c = Client()
        c.login(username='johndoe', password='illpassword')
        response = c.get('/')
        self.assertTrue(response.context["user"].is_authenticated())
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 0)

        ForceLogoutOrder.objects.force_logout(user)
        self.assertTrue(ForceLogoutOrder.objects.filter(user=user).exists())

        response = c.get('/')
        self.assertFalse(response.context["user"].is_authenticated())
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual('session_expired', messages[0].extra_tags)

        # Test relogin
        c.login(username='johndoe', password='illpassword')
        response = c.get('/')
        self.assertTrue(response.context["user"].is_authenticated())

    def test_force_logout_middleware_with_order_but_superuser(self):
        """
        Test if the ``ForceLogoutMiddleware`` work as excepted when a logout order is made but the user is admin.
        """
        user = get_user_model().objects.create_superuser(username='johndoe',
                                                         password='illpassword',
                                                         email='john.doe@example.com')

        with self.assertRaises(ForceLogoutOrder.DoesNotExist):
            ForceLogoutOrder.objects.get(user=user)

        c = Client()
        c.login(username='johndoe', password='illpassword')
        response = c.get('/')
        self.assertTrue(response.context["user"].is_authenticated())

        ForceLogoutOrder.objects.force_logout(user)
        self.assertTrue(ForceLogoutOrder.objects.filter(user=user).exists())

        response = c.get('/')
        self.assertTrue(response.context["user"].is_authenticated())

    def test_force_logout_middleware_with_order_but_no_session_key(self):
        """
        Test if the ``ForceLogoutMiddleware`` work as excepted when a logout order is made but the user does
        not have the session key with his login time set (for whatever reason).
        """
        user = get_user_model().objects.create_user(username='johndoe',
                                                    password='illpassword',
                                                    email='john.doe@example.com')

        with self.assertRaises(ForceLogoutOrder.DoesNotExist):
            ForceLogoutOrder.objects.get(user=user)

        c = Client()
        c.login(username='johndoe', password='illpassword')
        response = c.get('/')
        self.assertTrue(response.context["user"].is_authenticated())

        self.assertIsNotNone(c.session[FORCE_LOGOUT_SESSION_KEY])
        session = c.session
        session[FORCE_LOGOUT_SESSION_KEY] = None
        session.save()
        self.assertIsNone(c.session[FORCE_LOGOUT_SESSION_KEY])

        ForceLogoutOrder.objects.force_logout(user)
        self.assertTrue(ForceLogoutOrder.objects.filter(user=user).exists())

        response = c.get('/')
        self.assertTrue(response.context["user"].is_authenticated())
