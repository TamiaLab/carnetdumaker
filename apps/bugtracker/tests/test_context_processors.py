"""
Tests suite for the context processors of the bug tracker app.
"""

from django.test import SimpleTestCase
from django.http import HttpRequest

from ..context_processors import bugtracker
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


class BugTrackerContextProcessorTestCase(SimpleTestCase):
    """
    Tests case for the context processor.
    """

    def test_bugtracker_context_update(self):
        """
        Test if the ``bugtracker`` context processor add the constants into the context.
        """
        request = HttpRequest()
        result = bugtracker(request)
        self.assertEqual(result, {
            'BUGTRACKER_STATUS': {
                'OPEN': STATUS_OPEN,
                'NEED_DETAILS': STATUS_NEED_DETAILS,
                'CONFIRMED': STATUS_CONFIRMED,
                'WORKING_ON': STATUS_WORKING_ON,
                'DEFERRED': STATUS_DEFERRED,
                'DUPLICATE': STATUS_DUPLICATE,
                'WONT_FIX': STATUS_WONT_FIX,
                'CLOSED': STATUS_CLOSED,
                'FIXED': STATUS_FIXED,
            },

            'BUGTRACKER_PRIORITY': {
                'GODZILLA': PRIORITY_GODZILLA,
                'CRITICAL': PRIORITY_CRITICAL,
                'MAJOR': PRIORITY_MAJOR,
                'MINOR': PRIORITY_MINOR,
                'TRIVIAL': PRIORITY_TRIVIAL,
                'NEED_REVIEW': PRIORITY_NEED_REVIEW,
                'FEATURE': PRIORITY_FEATURE,
                'WISHLIST': PRIORITY_WISHLIST,
                'INVALID': PRIORITY_INVALID,
                'NOT_MY_FAULT': PRIORITY_NOT_MY_FAULT,
            },

            'BUGTRACKER_DIFFICULTY': {
                'DESIGN_ERRORS': DIFFICULTY_DESIGN_ERRORS,
                'IMPORTANT': DIFFICULTY_IMPORTANT,
                'NORMAL': DIFFICULTY_NORMAL,
                'LOW_IMPACT': DIFFICULTY_LOW_IMPACT,
                'OPTIONAL': DIFFICULTY_OPTIONAL,
            },
        })
