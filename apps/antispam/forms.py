"""
Forms mixin for the anti-spam app.
"""

import time

from django import forms
from django.utils import baseconv
from django.core.signing import Signer, BadSignature
from django.utils.translation import ugettext_lazy as _

from .settings import (MIN_TIME_FORM_GENERATION_SUBMIT,
                       MAX_TIME_FORM_GENERATION_SUBMIT,
                       DISABLE_ANTISPAM_VERIFICATION)


class AntispamHoneypotFormMixin(object):
    """
    Form mixin for adding anti-spam capabilities to any forms using an honeypot field and some clever tricks.
    """

    timestamp_signer_salt = 'saltisforpussybetterstartsniffingpepper'

    def __init__(self, *args, **kwargs):
        super(AntispamHoneypotFormMixin, self).__init__(*args, **kwargs)

        # Add anti-spam fields
        self.fields['comment'] = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 15}),
                                                 max_length=255,
                                                 required=False,
                                                 label=_('Leave this field blank'))

        self.fields['timestamp'] = forms.CharField(widget=forms.HiddenInput)

        # Generate timestamp
        self.initial['timestamp'] = self._generate_timestamp()

    def clean_comment(self):
        """
        Validate that the honeypot checkbox is NOT filled (robots killer).
        """
        if self.cleaned_data['comment'] and not DISABLE_ANTISPAM_VERIFICATION:
            raise forms.ValidationError(_('Are you a spam bot ? It seem, because you just fall in my trap.'),
                                        code='bot_trapped')
        return self.cleaned_data['comment']

    def clean(self):
        """
        Validate that the signed timestamp is not tampered and the timestamp is in allowed range.
        """
        cleaned_data = super(AntispamHoneypotFormMixin, self).clean()
        if 'timestamp' in cleaned_data:
            raw_timestamp = cleaned_data['timestamp']
            if not self._is_timestamp_valid(raw_timestamp):
                raise forms.ValidationError(_('Timestamp validation failed. Form was filled too quickly or too slowly. '
                                              'Please retry submitting the form.'),
                                            code='timestamp_failed')
        return cleaned_data

    def _generate_timestamp(self):
        """
        Generate a new signed timestamp.
        """
        signer = Signer(salt=self.timestamp_signer_salt)
        timestamp = baseconv.base62.encode(int(time.time()))
        return signer.sign(timestamp)

    def _is_timestamp_valid(self, timestamp):
        """
        Check if the given timestamp is valid.
        :param timestamp: The timestamp to be checked.
        :return: True if the timestamp is valid, False otherwise.
        """
        if DISABLE_ANTISPAM_VERIFICATION:
            return True
        signer = Signer(salt=self.timestamp_signer_salt)
        try:
            timestamp = signer.unsign(timestamp)
        except BadSignature:
            return False
        timestamp = baseconv.base62.decode(timestamp)
        age = int(time.time()) - timestamp
        return MIN_TIME_FORM_GENERATION_SUBMIT <= age <= MAX_TIME_FORM_GENERATION_SUBMIT
