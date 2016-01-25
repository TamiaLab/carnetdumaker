"""
Custom template tags for the text rendering app.
"""

from django.template import Library

from skcode.tools import escape_attrvalue as skcode_escape_attrvalue


register = Library()


@register.filter
def escape_attrvalue(value):
    """
    Escape the given value with the SkCode ``escape_attrvalue`` function.
    :param value: The attribute value to be escaped.
    :return: The escape string.
    """
    return skcode_escape_attrvalue(value)
