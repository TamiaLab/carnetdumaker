"""
Status and priority codes for the bug tracker app.
"""

from django.utils.translation import ugettext_lazy as _


STATUS_OPEN = 'open'
STATUS_REOPEN = 'reopen'
STATUS_NEED_DETAILS = 'needetails'
STATUS_CONFIRMED = 'confirmed'
STATUS_WORKING_ON = 'workon'
STATUS_DEFERRED = 'deferred'
STATUS_DUPLICATE = 'duplicate'
STATUS_WONT_FIX = 'wontfix'
STATUS_CLOSED = 'closed'
STATUS_FIXED = 'fixed'
STATUS_CODES = (
    (STATUS_OPEN, _('Issue open')),
    (STATUS_REOPEN, _('Issue reopened')),
    (STATUS_NEED_DETAILS, _('Need more details')),
    (STATUS_CONFIRMED, _('Issue confirmed')),
    (STATUS_WORKING_ON, _('Working on')),
    (STATUS_DEFERRED, _('Deferred (no time for that now)')),
    (STATUS_DUPLICATE, _('Duplicate issue')),
    (STATUS_WONT_FIX, _('Won\'t fix (sorry)')),
    (STATUS_CLOSED, _('Closed')),
    (STATUS_FIXED, _('Fixed')),
)


PRIORITY_GODZILLA = 'godzilla'  # We're doom!
PRIORITY_CRITICAL = 'critical'
PRIORITY_MAJOR = 'major'
PRIORITY_MINOR = 'minor'
PRIORITY_TRIVIAL = 'trivial'
PRIORITY_NEED_REVIEW = 'needreview'
PRIORITY_FEATURE = 'feature'
PRIORITY_WISHLIST = 'wishlist'
PRIORITY_INVALID = 'invalid'
PRIORITY_NOT_MY_FAULT = 'notmyfault'
PRIORITY_CODES = (
    (PRIORITY_GODZILLA, _('Godzilla (We\'re doomed!)')),
    (PRIORITY_CRITICAL, _('Critical (serious bug, need quick hotfix)')),
    (PRIORITY_MAJOR, _('Major (serious bug)')),
    (PRIORITY_MINOR, _('Minor (simple bug)')),
    (PRIORITY_TRIVIAL, _('Trivial (cosmetic issues)')),
    (PRIORITY_NEED_REVIEW, _('Need review')),
    (PRIORITY_FEATURE, _('Feature request')),
    (PRIORITY_WISHLIST, _('Wishlist request')),
    (PRIORITY_INVALID, _('Invalid')),
    (PRIORITY_NOT_MY_FAULT, _('Not my fault')),
)


DIFFICULTY_DESIGN_ERRORS = 'bigoops'
DIFFICULTY_IMPORTANT = 'important'
DIFFICULTY_NORMAL = 'normal'
DIFFICULTY_LOW_IMPACT = 'low'
DIFFICULTY_OPTIONAL = 'someday'
DIFFICULTY_CODES = (
    (DIFFICULTY_DESIGN_ERRORS, _('Design errors - back to the drawing board')),
    (DIFFICULTY_IMPORTANT, _('Important')),
    (DIFFICULTY_NORMAL, _('Normal')),
    (DIFFICULTY_LOW_IMPACT, _('Low')),
    (DIFFICULTY_OPTIONAL, _('Optional (will fix someday)')),
)
