"""
HTTP utilities.
"""

from django.http import HttpResponse
from django.utils.encoding import iri_to_uri


class HttpResponseReload(HttpResponse):
    """
    Reload page and stay on the same page from where request was made.
    Use the HTTP_REFERER meta value, or the ``fallback_uri`` argument value.
    """

    status_code = 302

    def __init__(self, request, fallback_uri='/'):
        HttpResponse.__init__(self)
        referrer = request.META.get('HTTP_REFERER')
        self['Location'] = iri_to_uri(referrer or fallback_uri)


def get_client_ip_address(request):
    """
    Return the first value of the HTTP_X_FORWARDED_FOR header if exist. Otherwise, return the value of the
    REMOTE_ADDR header instead.
    Remarks: HTTP server MUST cleanup the ``X-Forwarded-For`` header !
    Failing to sanitize the ``X-Forwarded-For`` header will allow IP spoofing, cause crash or make
    the app works with incorrect data (like 127.0.0.1).
    Example config for nginx: ``proxy_set_header X-Forwarded-For $remote_addr;``
    """
    ip_addr = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if ip_addr is not None:
        return ip_addr.split(', ')[0]
    else:
        return request.META.get('REMOTE_ADDR', None)
