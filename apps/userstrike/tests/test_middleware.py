"""
Tests suite for the user strike app.
"""

from django.test import TestCase, Client
from django.http import HttpRequest
from django.contrib.auth import get_user_model

from ..models import UserStrike
from ..middleware import UserStrikeMiddleware


class UserStrikeMiddlewareTestCase(TestCase):
    """
    Tests case for the ``UserStrikeMiddleware`` middleware.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.admin = get_user_model().objects.create_superuser(username='johndoe',
                                                               password='illpassword',
                                                               email='john.doe@example.com')
        self.user = get_user_model().objects.create_user(username='johnsmith',
                                                         password='illpassword',
                                                         email='john.smith@example.com')
        self.strike = UserStrike.objects.create(author=self.admin,
                                                internal_reason='Test strike',
                                                target_user=self.user)

    def test_middleware_installed(self):
        """
        Test if the ``UserStrikeMiddleware`` is installed.
        """
        from django.conf import settings
        self.assertIn('apps.userstrike.middleware.UserStrikeMiddleware', settings.MIDDLEWARE_CLASSES)

    def test_default_attr_name(self):
        """
        Test the default name value of the injected attribute.
        """
        mw = UserStrikeMiddleware()
        self.assertEqual('userstrike/access_blocked.html', mw.template_name)

    def test_cannot_strike_super_user(self):
        """
        The user strike middleware with a super user.
        """

        # Create a strike for a super admin
        UserStrike.objects.create(author=self.admin,
                                  internal_reason='Test strike super user',
                                  target_user=self.admin)

        # Test the middleware response
        request = HttpRequest()
        setattr(request, 'user', self.admin)

        mw = UserStrikeMiddleware()
        result = mw.process_request(request)
        self.assertIsNone(result)

    def test_middleware_with_authenticated_user(self):
        """
        The user strike middleware with an authenticated user.
        """
        client = Client()
        client.login(username='johnsmith', password='illpassword')

        response = client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertTemplateNotUsed(response, 'userstrike/access_blocked.html')
        self.assertIn('messages', response.context)
        messages = response.context['messages']
        self.assertEqual(1, len(messages))
        self.assertEqual('strike_warning', list(messages)[0].extra_tags)

    def test_middleware_with_authenticated_user_blocked(self):
        """
        The user strike middleware with an authenticated user (access blocked variant).
        """
        self.strike.block_access = True
        self.strike.save()

        client = Client()
        client.login(username='johnsmith', password='illpassword')

        response = client.get('/')
        self.assertEqual(403, response.status_code)
        self.assertTemplateUsed(response, 'userstrike/access_blocked.html')
        self.assertIn('strike', response.context)
        self.assertEqual(response.context['strike'], self.strike)

        messages = response.context['messages']
        self.assertEqual(0, len(messages))

    def test_middleware_ip_address(self):
        """
        The user strike middleware with an IP address.
        """
        UserStrike.objects.create(author=self.admin,
                                  internal_reason='Test strike',
                                  target_ip_address='10.0.0.2')
        get_user_model().objects.create_user(username='anonymous',
                                             password='illpassword',
                                             email='anonymous@example.com')

        client = Client(REMOTE_ADDR='10.0.0.2')
        client.login(username='anonymous', password='illpassword')

        response = client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertTemplateNotUsed(response, 'userstrike/access_blocked.html')
        self.assertIn('messages', response.context)
        messages = response.context['messages']
        self.assertEqual(1, len(messages))
        self.assertEqual('strike_warning', list(messages)[0].extra_tags)

    def test_middleware_ip_address_blocked(self):
        """
        The user strike middleware with an IP address.
        """
        ip_strike = UserStrike.objects.create(author=self.admin,
                                              internal_reason='Test strike',
                                              target_ip_address='10.0.0.2',
                                              block_access=True)
        get_user_model().objects.create_user(username='anonymous',
                                             password='illpassword',
                                             email='anonymous@example.com')

        client = Client(REMOTE_ADDR='10.0.0.2')
        client.login(username='anonymous', password='illpassword')

        response = client.get('/')
        self.assertEqual(403, response.status_code)
        self.assertTemplateUsed(response, 'userstrike/access_blocked.html')
        self.assertIn('strike', response.context)
        self.assertEqual(response.context['strike'], ip_strike)

        messages = response.context['messages']
        self.assertEqual(0, len(messages))

    def test_middleware_idle(self):
        """
        The user strike middleware with nothing to do.
        """
        UserStrike.objects.create(author=self.admin,
                                  internal_reason='Test strike',
                                  target_ip_address='10.0.0.2')
        get_user_model().objects.create_user(username='anonymous',
                                             password='illpassword',
                                             email='anonymous@example.com')

        client = Client(REMOTE_ADDR='192.168.1.1')
        client.login(username='anonymous', password='illpassword')

        response = client.get('/')
        self.assertEqual(200, response.status_code)

        messages = response.context['messages']
        self.assertEqual(0, len(messages))
