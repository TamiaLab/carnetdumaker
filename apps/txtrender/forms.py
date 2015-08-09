"""
Custom form fields for the text rendering app.
"""

from django import forms

from .fields import RenderTextFieldBase
from .widgets import MarkupEditorTextarea


class MarkupCharField(forms.CharField):
    """
    Simple subclass or ```forms.CharField`` with the ``help_text`` pre-filled.
    """

    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = MarkupEditorTextarea
        if 'help_text' not in kwargs:
            kwargs['help_text'] = RenderTextFieldBase.HELP_TEXT
        super(MarkupCharField, self).__init__(*args, **kwargs)
