"""
Custom template tags for the bootstrap forms app.
"""

from django import forms
from django.template import Context
from django.template.loader import get_template
from django import template


register = template.Library()


@register.filter
def bootstrapform(element, bootstrap_type='vertical'):
    """
    Render a bootstrap form or form's field.
    :param element: The form or form's field to be rendered.
    :param bootstrap_type: The type of bootstrap form. Can be "inline", "vertical" (default), or "horizontal".
    """
    element_type = element.__class__.__name__.lower()
    template_var = 'form'
    if element_type == 'boundfield':
        add_input_classes(element)
        template = get_template('bootstrapform/field.html')
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)
            template = get_template("bootstrapform/formset.html")
            template_var = 'formset'
        else:
            for field in element.visible_fields():
                add_input_classes(field)
            template = get_template('bootstrapform/form.html')
    context = Context({template_var: element, 'bootstrap_type': bootstrap_type})
    return template.render(context)


def add_input_classes(field):
    """
    Add the CSS class ``form-control`` to any unknown field type.
    Known field types will have the class attribute set using template.
    :param field: The field to be processed.
    """
    if not is_checkbox(field) and \
            not is_multiple_checkbox(field) and \
            not is_radio(field) and \
            not is_file(field):
        field_classes = field.field.widget.attrs.get('class', '')
        field_classes += ' form-control'
        field.field.widget.attrs['class'] = field_classes


@register.filter
def is_checkbox(field):
    """
    Return ``True`` if the given field instance is an ``CheckboxInput``.
    :param field: The field to be tested.
    """
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    """
    Return ``True`` if the given field instance is an ``CheckboxSelectMultiple``.
    :param field: The field to be tested.
    """
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    """
    Return ``True`` if the given field instance is an ``RadioSelect``.
    :param field: The field to be tested.
    """
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    """
    Return ``True`` if the given field instance is an ``FileInput``.
    :param field: The field to be tested.
    """
    return isinstance(field.field.widget, forms.FileInput)
