"""
Model fields for the countries app.
"""

from django.db import models
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from .countries import COUNTRIES_CHOICES


class CountryFieldBase(models.CharField):
    """
    This database model field can be used to store the name of a country.
    """

    description = _('A country name object')

    MAX_LENGTH = 3

    def __init__(self, *args, **kwargs):
        parent_kwargs = {
            'max_length': self.MAX_LENGTH,
            'choices': COUNTRIES_CHOICES,
            }
        parent_kwargs.update(kwargs)
        super(CountryFieldBase, self).__init__(*args, **parent_kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(CountryFieldBase, self).deconstruct()
        if kwargs['choices'] == COUNTRIES_CHOICES:
            del kwargs['choices']
        if kwargs['max_length'] == self.MAX_LENGTH:
            del kwargs['max_length']
        return name, path, args, kwargs

    def get_internal_type(self):
        return "CharField"


class CountryField(six.with_metaclass(models.SubfieldBase,
                                      CountryFieldBase)):
    """
    Database Country field. Can be used to store a country name.
    See ``CountryFieldBase`` for details.
    """
    pass