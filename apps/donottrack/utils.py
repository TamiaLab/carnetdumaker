"""
Utilities for the DoNotTrack app.
"""


def get_do_not_track_flag(request):
    """
    Returns the status of the ``DNT`` flag header.
    :param request: The current request instance.
    :return: ``True`` if the ``DNT`` flag header is set, ``False`` otherwise.
    """
    return request.META.get('HTTP_DNT') == '1'
