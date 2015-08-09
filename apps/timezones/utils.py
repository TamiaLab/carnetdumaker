"""
Various shortcut and tools functions for the timezones app.
"""

import pytz


def is_pytz_instance(value):
    """
    Return true if ``value`` is equal to pytz.UTC (singleton), or if ``value``
    is an instance of ``pytz.tzinfo.BaseTzInfo`` (or child classes).
    :param value: pytz.tzinfo.BaseTzInfo
    :return: bool
    """
    return value is pytz.UTC or isinstance(value, pytz.tzinfo.BaseTzInfo)
