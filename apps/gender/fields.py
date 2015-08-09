"""
Model fields for the gender app.
"""

from django.db import models
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from .constants import (GENDER_CHOICES,
                        GENDER_UNKNOWN)


class GenderFieldBase(models.CharField):
    """
    This database model field can be used to store the gender of a person.
    """

    description = _('A gender type object')

    MAX_LENGTH = 1

    def __init__(self, *args, **kwargs):
        parent_kwargs = {
            'max_length': self.MAX_LENGTH,
            'choices': GENDER_CHOICES,
            'default': GENDER_UNKNOWN,
            'blank': True,
            }
        parent_kwargs.update(kwargs)
        super(GenderFieldBase, self).__init__(*args, **parent_kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(GenderFieldBase, self).deconstruct()
        if kwargs['choices'] == GENDER_CHOICES:
            del kwargs['choices']
        if kwargs['max_length'] == self.MAX_LENGTH:
            del kwargs['max_length']
        if kwargs['default'] == GENDER_UNKNOWN:
            del kwargs['default']
        if kwargs['blank']:
            del kwargs['blank']
        return name, path, args, kwargs

    def get_internal_type(self):
        return "CharField"


class GenderField(six.with_metaclass(models.SubfieldBase,
                                     GenderFieldBase)):
    """
    Database gender field. Can be used to store a gender type.
    See ``GenderFieldBase`` for details.
    """
    pass
