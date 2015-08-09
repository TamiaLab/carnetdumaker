"""
Genders list for the gender app.
"""

from django.utils.translation import ugettext_lazy as _


GENDER_MALE = 'M'
GENDER_FEMALE = 'F'
GENDER_OTHER = 'O'
GENDER_UNKNOWN = ''

GENDER_CHOICES = (
    (GENDER_MALE, _('Male')),
    (GENDER_FEMALE, _('Female')),
    (GENDER_OTHER, _('Other')),
    (GENDER_UNKNOWN, _('Unspecified'))
)
