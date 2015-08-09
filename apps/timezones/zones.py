"""
Timezones lists for the timezones app.
"""

import pytz
from datetime import datetime
from operator import itemgetter


def prettify_tz(tz_name):
    """
    Return the given timezone name in the "(UTC−hhmm) TZNAME" format.
    :param tz_name: The timezone name as string.
    :return: The prettyfied timezone name in the format "(UTC+hhmm) TZNAME" or "(UTC−hhmm) TZNAME".
    """
    now = datetime.now(pytz.timezone(tz_name))
    utc_offset_str = now.strftime('%z')
    return '(UTC%s) %s' % (utc_offset_str, tz_name)


# All known timezones from pytz - INCLUDED DEPRECATED TIMEZONES
ALL_TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

# Common timezones from pytz
COMMON_TIMEZONE_CHOICES = tuple(zip(pytz.common_timezones, pytz.common_timezones))

# Common timezones in "(UTC−hhmm) TZNAME" format and sorted in natural order - RECOMMENDED
PRETTY_TIMEZONE_CHOICES = tuple(zip(pytz.common_timezones, [prettify_tz(tz_name) for tz_name in pytz.common_timezones]))
PRETTY_TIMEZONE_CHOICES = sorted(PRETTY_TIMEZONE_CHOICES, key=itemgetter(1))
