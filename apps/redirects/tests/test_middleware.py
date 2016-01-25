"""
Tests suite for the redirect app.
"""

from django.conf import settings
from django.http import HttpResponse
from django.test import TestCase, Client

from ..models import Redirection
from ..middleware import RedirectFallbackMiddleware


class RedirectFallbackMiddlewareTestCase(TestCase):
    """
    Tests suite for the ``RedirectFallbackMiddleware``.
    """

    def test_middleware_installed(self):
        """
        Test if the ``RedirectFallbackMiddleware`` is installed.
        """
        from django.conf import settings
        self.assertIn('apps.redirects.middleware.RedirectFallbackMiddleware', settings.MIDDLEWARE_CLASSES)

    def test_without_404(self):
        """
        Test the middleware when status is NOT 404.
        """
        mw = RedirectFallbackMiddleware()
        response = HttpResponse()
        self.assertEqual(200, response.status_code)
        ret = mw.process_response(None, response)
        self.assertEqual(response, ret)

    def test_permanent_redirection(self):
        """
        Test the middleware with a permanent redirection..
        """
        Redirection.objects.create(site_id=settings.SITE_ID,
                                   old_path='/test-RedirectFallbackMiddleware/',
                                   new_path='/test-RedirectFallbackMiddleware-2/')
        client = Client()
        response = client.get('/test-RedirectFallbackMiddleware/')
        self.assertRedirects(response, '/test-RedirectFallbackMiddleware-2/',
                             status_code=301, fetch_redirect_response=False)

    def test_temporary_redirection(self):
        """
        Test the middleware with a temporary redirection.
        """
        Redirection.objects.create(site_id=settings.SITE_ID,
                                   old_path='/test-RedirectFallbackMiddleware/',
                                   new_path='/test-RedirectFallbackMiddleware-2/',
                                   permanent_redirect=False)
        client = Client()
        response = client.get('/test-RedirectFallbackMiddleware/')
        self.assertRedirects(response, '/test-RedirectFallbackMiddleware-2/',
                             status_code=302, fetch_redirect_response=False)

    def test_gone_redirection(self):
        """
        Test the middleware with a gone redirection.
        """
        Redirection.objects.create(site_id=settings.SITE_ID,
                                   old_path='/test-RedirectFallbackMiddleware/',
                                   new_path='')
        client = Client()
        response = client.get('/test-RedirectFallbackMiddleware/')
        self.assertEqual(410, response.status_code)
        self.assertTemplateUsed(response, '410.html')

    def test_no_redirection(self):
        """
        Test the middleware with no redirection.
        """
        self.assertEqual(0, Redirection.objects.count())
        client = Client()
        response = client.get('/test-RedirectFallbackMiddleware/')
        self.assertEqual(404, response.status_code)
