"""
Middleware for the redirect app.
"""

from django import http
from django.apps import apps
from django.conf import settings
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.shortcuts import get_current_site

from .models import Redirection


class RedirectFallbackMiddleware(object):
    """
    Runtime 404 redirection handling middleware.
    """

    # Defined as class-level attributes to be subclassing-friendly.
    response_gone_template_name = '410.html'
    response_redirect_class = http.HttpResponseRedirect
    response_permanent_redirect_class = http.HttpResponsePermanentRedirect

    def __init__(self):
        """
        Check if the ``sites`` framework is installed.
        """

        # Site framework is required
        if not apps.is_installed('django.contrib.sites'):
            raise ImproperlyConfigured(
                    "You cannot use RedirectFallbackMiddleware when "
                    "django.contrib.sites is not installed."
            )

    def process_response(self, request, response):
        """
        Process the response. Do something only if the status code is 404.
        :param request: The current request.
        :param response: The current response.
        """

        # No need to check for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        # Get the current request site object
        current_site = get_current_site(request)

        # Query the database
        r = Redirection.objects.get_redirection(current_site, request)

        # Handle the redirection
        if r is not None:
            if not r.new_path:
                return render(request, self.response_gone_template_name, {}, status=410)
            elif r.permanent_redirect:
                return self.response_permanent_redirect_class(r.new_path)
            else:
                return self.response_redirect_class(r.new_path)

        # No redirect was found. Return the response.
        return response
