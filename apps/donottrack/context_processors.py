"""
Context processors for the DoNotTrack app.
"""

from .utils import get_do_not_track_flag


def do_not_track(request):
    """
    Adds ``DO_NOT_TRACK`` (bool) to the context, which is ``True`` if the ``DNT``
    flag header is set, ``False`` otherwise.
    :param request: The current request instance.
    :return: A dict with the ``DO_NOT_TRACK``: bool item.
    """
    return {
        'DO_NOT_TRACK': get_do_not_track_flag(request),
    }
