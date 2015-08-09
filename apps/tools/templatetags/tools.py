"""
Custom template tags for the private messages app.
"""

from django.utils.translation import ugettext as _
from django.template import Library, defaultfilters
from django.utils.html import mark_safe


register = Library()


@register.filter
def date_html(datetime):
    """
    Output an HTML tag (marked safe) like this :
    ``<time datetime="%(date_iso)s %(time_iso)s">%(date_locale)s</time>``
    :param datetime: The datetime object to be displayed.
    :return: A safe string like ``<time datetime="%(date_iso)s %(time_iso)s">%(date_locale)s</time>``
    """
    context = {
        'date_iso': defaultfilters.date(datetime, 'd-m-Y'),
        'time_iso': defaultfilters.time(datetime, 'H:i'),
        'date_locale': defaultfilters.date(datetime),
    }
    return mark_safe('<time datetime="%(date_iso)s %(time_iso)s">%(date_locale)s</time>' % context)


@register.filter
def datetime_html(datetime):
    """
    Output an HTML tag (marked safe) like this :
    ``<time datetime="%(date_iso)s %(time_iso)s">%(date_locale)s</time>``
    :param datetime: The datetime object to be displayed.
    :return: A safe string like ``<time datetime="%(date_iso)s %(time_iso)s">%(date_locale)s</time>``
    """
    context = {
        'date_iso': defaultfilters.date(datetime, 'd-m-Y'),
        'time_iso': defaultfilters.time(datetime, 'H:i'),
        'date_locale': defaultfilters.date(datetime),
        'time_locale': defaultfilters.time(datetime),
        # Translators: This is used to make a sentence like "June 12 2015 AT 8:30 AM"
        'at_str': _('at'),
    }
    return mark_safe('<time datetime="%(date_iso)s %(time_iso)s">%(date_locale)s %(at_str)s %(time_locale)s</time>' % context)