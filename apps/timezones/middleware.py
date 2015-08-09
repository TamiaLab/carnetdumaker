"""
Middleware for the timezone selection.
"""

import pytz

from django.utils import timezone


TIMEZONE_SESSION_KEY = 'django_timezone'


class TimezoneMiddleware(object):
    """
    Middleware for automatic timezone selection using session data.
    If ``TIMEZONE_SESSION_KEY`` is defined in the session keystore, the specified timezone will be activated.
    """

    def process_request(self, request):
        """
        Process the request, activate the timezone in ``request.session[TIMEZONE_SESSION_KEY]`` if
        defined.
        :param request: The incoming request
        :return: None
        """
        tzname = request.session.get(TIMEZONE_SESSION_KEY)
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
