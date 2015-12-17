"""
Model fields for the text rendering app.
"""

from django.db import models
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminTextareaWidget

from .widgets import (RichTextEditorTextarea,
                      AdminRichTextEditorTextarea)


class RenderTextFieldBase(models.TextField):
    """
    This database model field is a simple wrapper around the ``TextField`` class allowing factoring of help text for
    all rendered text fields in model.
    """

    description = _('A rendered text string')

    HELP_TEXT = _('You can use BBCode in this field.')

    def __init__(self, *args, **kwargs):
        parent_kwargs = {
            'help_text': self.HELP_TEXT,
            'default': '',
            'blank': True,
        }
        parent_kwargs.update(kwargs)
        super(RenderTextFieldBase, self).__init__(*args, **parent_kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RenderTextFieldBase, self).deconstruct()
        if kwargs['help_text'] == self.HELP_TEXT:
            del kwargs['help_text']
        if kwargs['default'] == '':
            del kwargs['default']
        if kwargs['blank']:
            del kwargs['blank']
        return name, path, args, kwargs

    def get_internal_type(self):
        return "TextField"

    def formfield(self, **kwargs):
        defaults = {'widget': RichTextEditorTextarea}
        defaults.update(kwargs)

        # As an ugly hack, we override the admin widget
        if defaults['widget'] == AdminTextareaWidget:
            defaults['widget'] = AdminRichTextEditorTextarea

        return super(RenderTextFieldBase, self).formfield(**defaults)


class RenderTextField(six.with_metaclass(models.SubfieldBase,
                                         RenderTextFieldBase)):
    """
    Database text field with extra rendering option.
    See ``RenderTextFieldBase`` for details.
    """
    pass
