"""
Custom template tags for the bug tracker app.
"""

from django import template
from django.template.defaultfilters import stringfilter

from ..constants import (STATUS_OPEN,
                         STATUS_NEED_DETAILS,
                         STATUS_CONFIRMED,
                         STATUS_WORKING_ON,
                         STATUS_DEFERRED,
                         STATUS_DUPLICATE,
                         STATUS_WONT_FIX,
                         STATUS_CLOSED,
                         STATUS_FIXED)
from ..constants import (PRIORITY_GODZILLA,
                         PRIORITY_CRITICAL,
                         PRIORITY_MAJOR,
                         PRIORITY_MINOR,
                         PRIORITY_TRIVIAL,
                         PRIORITY_NEED_REVIEW,
                         PRIORITY_FEATURE,
                         PRIORITY_WISHLIST,
                         PRIORITY_INVALID,
                         PRIORITY_NOT_MY_FAULT)
from ..constants import (DIFFICULTY_DESIGN_ERRORS,
                         DIFFICULTY_IMPORTANT,
                         DIFFICULTY_NORMAL,
                         DIFFICULTY_LOW_IMPACT,
                         DIFFICULTY_OPTIONAL)


register = template.Library()


@register.filter
def can_edit_ticket(user, ticket):
    """
    Return True if the given user can edit the given ticket.
    :param user: The target user.
    :param ticket: The target ticket.
    :return: True if the given user can edit the given ticket.
    """
    if user is None or ticket is None:
        return False
    return ticket.can_edit(user)


@register.filter
@stringfilter
def color_status(status):
    """
    Get the bootstrap's label class name for the given status code.
    Color scheme:
    - OPEN or NEED_DETAILS: danger (red = need attention),
    - CONFIRMED: warning (orange = be aware, will be fixed soon),
    - WORKING_ON: info (blue = don't disturb me)
    - FIXED or CLOSED: success (green = no problem),
    - WONT_FIX, DUPLICATE or DEFERRED: default (gray = f*ck it),
    Return an empty string on erroneous status code.
    :param status: The code status to be coloured.
    :return The bootstrap label class name for the given status code.
    """
    color = ''
    if status == STATUS_FIXED or status == STATUS_CLOSED:
        color = 'success'
    elif status == STATUS_OPEN or status == STATUS_NEED_DETAILS:
        color = 'danger'
    elif status == STATUS_WONT_FIX or status == STATUS_DUPLICATE or status == STATUS_DEFERRED:
        color = 'default'
    elif status == STATUS_CONFIRMED:
        color = 'warning'
    elif status == STATUS_WORKING_ON:
        color = 'info'
    return color


@register.filter
@stringfilter
def color_priority(priority):
    """
    Get the bootstrap's label class name for the given priority code.
    Color scheme:
    - NEED_REVIEW: default (gray = don't known yet)
    - GODZILLA or CRITICAL: danger (red = need attention NOW),
    - MAJOR: warning (orange = need attention ASAP),
    - MINOR: primary (dark blue = someday),
    - TRIVIAL: info (blue = someday),
    - WISHLIST, FEATURE, NOT_MY_FAULT or INVALID: success (green = no more problem)
    Return an empty string on erroneous priority code.
    :param priority: The code priority to be coloured.
    :return The bootstrap label class name for the given priority code.
    """
    color = ''
    if priority == PRIORITY_GODZILLA or priority == PRIORITY_CRITICAL:
        color = 'danger'
    elif priority == PRIORITY_MAJOR:
        color = 'warning'
    elif priority == PRIORITY_MINOR:
        color = 'primary'
    elif priority == PRIORITY_TRIVIAL:
        color = 'info'
    elif priority == PRIORITY_NEED_REVIEW:
        color = 'default'
    elif (priority == PRIORITY_WISHLIST or priority == PRIORITY_FEATURE
          or priority == PRIORITY_NOT_MY_FAULT or priority == PRIORITY_INVALID):
        color = 'success'
    return color


@register.filter
@stringfilter
def color_difficulty(difficulty):
    """
    Get the bootstrap's label class name for the given difficulty code.
    Color scheme:
    - DESIGN_ERRORS: danger (red = very complicated),
    - IMPORTANT: warning (orange = complicated but not too much),
    - NORMAL: success (green = just complicated as normal)
    - LOW_IMPACT: info (blue = not complicated at all)
    - OPTIONAL: default (gray = f*ck it, someday),
    Return an empty string on erroneous difficulty code.
    :param difficulty: The code difficulty to be coloured.
    :return The bootstrap label class name for the given difficulty code.
    """
    color = ''
    if difficulty == DIFFICULTY_DESIGN_ERRORS:
        color = 'danger'
    elif difficulty == DIFFICULTY_IMPORTANT:
        color = 'warning'
    elif difficulty == DIFFICULTY_NORMAL:
        color = 'success'
    elif difficulty == DIFFICULTY_LOW_IMPACT:
        color = 'info'
    elif difficulty == DIFFICULTY_OPTIONAL:
        color = 'default'
    return color
