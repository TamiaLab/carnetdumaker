"""
Middleware for the force-logout app.
"""

from django.contrib import auth
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from .models import (ForceLogoutOrder,
                     FORCE_LOGOUT_SESSION_KEY)


class ForceLogoutMiddleware(object):
    """
    Middleware for login-out user if requested by admin.
    """

    def process_request(self, request):
        """
        Process the request, logout the user if necessary.
        :param request: The incoming request
        :return: None
        """

        # Only handle authenticated users
        if not request.user.is_authenticated():
            return

        # Super admin cannot be kicked out
        if request.user.is_superuser:
            return

        # Get the login time from the session
        login_time = request.session.get(FORCE_LOGOUT_SESSION_KEY, None)

        # Don't logout user if the login signal has failed
        if login_time is None:
            return

        # Get the logout order if any
        try:
            logout_order = ForceLogoutOrder.objects.get(user=request.user)
        except ForceLogoutOrder.DoesNotExist:
            return

        # If the order is valid, BOOM
        if logout_order.order_date.timestamp() > login_time:
            auth.logout(request)
            messages.add_message(request, messages.INFO, _('Your session has expired.'), extra_tags='session_expired')
