"""
Forms for the user API keys app.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _


class KeyRegenerationConfirmationForm(forms.Form):
    """
    Simple confirmation form for the key regeneration view.
    """

    confirm = forms.BooleanField(label=_("I want to regenerate my API key and understand "
                                         "doing this will invalidate previous ones."),
                                 required=True,
                                 initial=False)
