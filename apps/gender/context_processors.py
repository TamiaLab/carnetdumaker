"""
Extra context processors for the gender app.
"""

from .constants import (GENDER_FEMALE,
                        GENDER_MALE,
                        GENDER_UNKNOWN,
                        GENDER_OTHER)


def gender(request):
    """
    Constants context processor.
    :param request: the current request.
    :return: All gender codes as constants.
    """
    return {
        'GENDER': {
            'FEMALE': GENDER_FEMALE,
            'MALE': GENDER_MALE,
            'OTHER': GENDER_OTHER,
            'UNKNOWN': GENDER_UNKNOWN,
        },
    }
