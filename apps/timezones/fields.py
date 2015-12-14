"""
Model fields for the timezones app.
"""

import pytz

from django.db import models
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .utils import is_pytz_instance
from .zones import COMMON_TIMEZONE_CHOICES


class TimeZoneFieldBase(models.Field):
    """
    Provides database store for pytz timezone objects.
    Valid inputs are:
    - any instance of ``pytz.tzinfo.DstTzInfo`` or ``pytz.tzinfo.StaticTzInfo``
    - the ``pytz.UTC`` singleton
    - any string that validates against pytz.common_timezones.
    - None and the empty string both represent 'no timezone'
    Valid outputs:
    - None
    - instances of ``pytz.tzinfo.DstTzInfo`` and ``pytz.tzinfo.StaticTzInfo``
    - the ``pytz.UTC`` singleton
    """

    description = _('A pytz timezone object')

    MAX_LENGTH = 63

    def __init__(self, *args, **kwargs):
        parent_kwargs = {
            'max_length': self.MAX_LENGTH,
            'choices': COMMON_TIMEZONE_CHOICES,
            'null': True,
        }
        parent_kwargs.update(kwargs)
        super(TimeZoneFieldBase, self).__init__(*args, **parent_kwargs)

    def validate(self, value, model_instance):
        # since our choices are of the form [<str>, <str>], convert the
        # incoming value to a string for validation
        if not is_pytz_instance(value):
            raise ValidationError('"%s" is not a pytz timezone object' % value)
        tz_as_str = value.zone
        super(TimeZoneFieldBase, self).validate(tz_as_str, model_instance)

    def deconstruct(self):
        name, path, args, kwargs = super(TimeZoneFieldBase, self).deconstruct()
        if kwargs['choices'] == COMMON_TIMEZONE_CHOICES:
            del kwargs['choices']
        if kwargs['max_length'] == self.MAX_LENGTH:
            del kwargs['max_length']
        if kwargs['null'] is True:
            del kwargs['null']
        return name, path, args, kwargs

    def get_internal_type(self):
        return 'CharField'

    def to_python(self, value):
        """ Convert value to a pytz timezone object """
        return self._get_python_and_db_repr(value)[0]

    def get_prep_value(self, value):
        """ Convert value a to string describing a valid pytz timezone object """
        return self._get_python_and_db_repr(value)[1]

    def _get_python_and_db_repr(self, value):
        """ Returns a tuple of (python representation, db representation) """
        if value is None or value == '':
            return None, None
        if is_pytz_instance(value):
            return value, value.zone
        if isinstance(value, six.string_types):
            try:
                return pytz.timezone(value), value
            except pytz.UnknownTimeZoneError:
                pass
        raise ValidationError("Invalid timezone '%s'" % value)


class TimeZoneField(six.with_metaclass(models.SubfieldBase,
                                       TimeZoneFieldBase)):
    """
    Database TimeZone field. Can be used to store a pytz timezone.
    See ``TimeZoneFieldBase`` for details.
    """
    pass
