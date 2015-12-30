"""
Tests suite for the template tags of the bug tracker app.
"""

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from ..templatetags.bugtracker import (can_edit_ticket,
                                       color_status,
                                       color_priority,
                                       color_difficulty)
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


class BugTrackerTemplateTagsTestCase(SimpleTestCase):
    """
    Tests suite for the template tags of the bug tracker app.
    """

    def test_can_edit_ticket_true(self):
        """
        Test the ``can_edit_ticket`` filter with can_edit=True.
        """
        user = MagicMock()
        ticket = MagicMock()
        ticket.can_edit.return_value = True
        self.assertTrue(can_edit_ticket(user, ticket))
        ticket.can_edit.assert_called_once_with(user)

    def test_can_edit_ticket_false(self):
        """
        Test the ``can_edit_ticket`` filter with can_edit=False.
        """
        user = MagicMock()
        ticket = MagicMock()
        ticket.can_edit.return_value = False
        self.assertFalse(can_edit_ticket(user, ticket))
        ticket.can_edit.assert_called_once_with(user)

    def test_can_edit_ticket_none(self):
        """
        Test the ``can_edit_ticket`` filter with some none values.
        """
        user = MagicMock()
        ticket = MagicMock()
        self.assertFalse(can_edit_ticket(None, ticket))
        self.assertFalse(can_edit_ticket(user, None))
        self.assertFalse(can_edit_ticket(None, None))

    def test_color_status(self):
        """
        Test the ``color_status`` filter.
        """
        self.assertEqual('danger', color_status(STATUS_OPEN))
        self.assertEqual('danger', color_status(STATUS_NEED_DETAILS))
        self.assertEqual('warning', color_status(STATUS_CONFIRMED))
        self.assertEqual('info', color_status(STATUS_WORKING_ON))
        self.assertEqual('default', color_status(STATUS_DEFERRED))
        self.assertEqual('default', color_status(STATUS_DUPLICATE))
        self.assertEqual('default', color_status(STATUS_WONT_FIX))
        self.assertEqual('success', color_status(STATUS_CLOSED))
        self.assertEqual('success', color_status(STATUS_FIXED))
        self.assertEqual('', color_status('xyz'))

    def test_color_priority(self):
        """
        Test the ``color_priority`` filter.
        """
        self.assertEqual('danger', color_priority(PRIORITY_GODZILLA))
        self.assertEqual('danger', color_priority(PRIORITY_CRITICAL))
        self.assertEqual('warning', color_priority(PRIORITY_MAJOR))
        self.assertEqual('primary', color_priority(PRIORITY_MINOR))
        self.assertEqual('info', color_priority(PRIORITY_TRIVIAL))
        self.assertEqual('default', color_priority(PRIORITY_NEED_REVIEW))
        self.assertEqual('success', color_priority(PRIORITY_FEATURE))
        self.assertEqual('success', color_priority(PRIORITY_WISHLIST))
        self.assertEqual('success', color_priority(PRIORITY_INVALID))
        self.assertEqual('success', color_priority(PRIORITY_NOT_MY_FAULT))
        self.assertEqual('', color_priority('xyz'))

    def test_color_difficulty(self):
        """
        Test the ``color_difficulty`` filter.
        """
        self.assertEqual('danger', color_difficulty(DIFFICULTY_DESIGN_ERRORS))
        self.assertEqual('warning', color_difficulty(DIFFICULTY_IMPORTANT))
        self.assertEqual('success', color_difficulty(DIFFICULTY_NORMAL))
        self.assertEqual('info', color_difficulty(DIFFICULTY_LOW_IMPACT))
        self.assertEqual('default', color_difficulty(DIFFICULTY_OPTIONAL))
        self.assertEqual('', color_difficulty('xyz'))
