"""
Forms fields for the timezones app.
"""

import pytz

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .zones import PRETTY_TIMEZONE_CHOICES


def coerce_to_pytz(val):
    """
    Transform a string timezone to a pytz timezone instance.
    :param val: str
    :return pytz.tzinfo
    """
    try:
        return pytz.timezone(val)
    except pytz.UnknownTimeZoneError:
        raise ValidationError(_('Unknown timezone "%s"') % val)


class TimezoneFormField(forms.TypedChoiceField):
    """
    Timezone form field, list all common timezones in a pretty format
    and allow user to select one timezone. The timezone is automatically
    converted into a ``tzinfo`` instance at reading.
    """

    def __init__(self, *args, **kwargs):
        defaults = {
            'coerce': coerce_to_pytz,
            'choices': PRETTY_TIMEZONE_CHOICES,
            'empty_value': None,
            }
        defaults.update(kwargs)
        super(TimezoneFormField, self).__init__(*args, **defaults)
