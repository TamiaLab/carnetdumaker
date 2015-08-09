"""
Custom forms widgets for the bootstrap forms app.
"""

from django.utils import formats
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.forms.widgets import Widget
from django.forms.utils import flatatt


class StaticControlInput(Widget):
    """
    A bootstrap dependent static control. Simply display as ``<p>``.
    To be used with ``forms.Field`` directly. Do not forget to set the initial value and the label.
    """

    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            value = force_text(self._format_value(value))
        return format_html('<p{1}>{0}</p>', value, flatatt(final_attrs))
