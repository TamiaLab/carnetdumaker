"""
Middleware for the DoNotTrack app.
"""

from django.utils.cache import patch_vary_headers

from .utils import get_do_not_track_flag


class DoNotTrackMiddleware(object):
    """
    Middleware injecting the current ``DNT`` flag header status into the request object for other apps.
    Use ``request.do_not_track`` (bool) to check the flag. This middleware also update the ``Vary`` HTTP header
    for DNT + caching support.
    """

    # Attribute name in the request object of the injected bool
    do_not_track_attr_name = 'do_not_track'

    def process_request(self, request):
        """
        Inject the current ``DNT`` flag header status into the request object for other apps.
        :param request: The current request instance.
        :return: Always ``None`` to let Django continue the processing of the request.
        """

        # Inject the bool flag in the request object
        do_not_track_flag = get_do_not_track_flag(request)
        setattr(request, self.do_not_track_attr_name, do_not_track_flag)

        # Continue processing of request
        return None

    def process_response(self, request, response):
        """
        Adds a vary header for ``DNT``, allowing cache control based on the ``DNT`` flag header.
        :param request: The current request instance.
        :param response: The current response instance.
        :return: Always ``response`` to let Django continue the processing of the response.
        """

        # Patch Vary header
        patch_vary_headers(response, ('DNT', ))

        # Continue processing of response
        return response
