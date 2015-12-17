"""
Custom forms widget for the text rendering app.
Use http://markitup.jaysalvat.com/home/ for the client-side editing front end.
"""

from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget


class MarkupEditorTextarea(forms.Textarea):
    """
    MarkitUp editor widget.
    """

    SETTINGS_VARNAME = 'mySettings'

    def render(self, name, value, attrs=None):
        textarea_html = super(MarkupEditorTextarea, self).render(name, value, attrs)
        script_html = """<script type="text/javascript" >
    $(document).ready(function() {
        $("#%(textarea_id)s").markItUp(%(settings_varname)s);
    });
</script>\n""" % {'textarea_id': attrs.get('id', 'id_%s' % name), 'settings_varname': self.SETTINGS_VARNAME}
        return script_html + textarea_html

    class Media:
        css = {
            'all': ('css/font-awesome.min.css',
                    'markitup/sets/html/style.css',
                    'markitup/skins/simple/style.css')
        }
        js = ('markitup/jquery.markitup.js',
              'markitup/sets/html/set.js')


class AdminMarkupEditorTextarea(MarkupEditorTextarea, AdminTextareaWidget):
    """
    Django-admin version of ``MarkupEditorTextarea``.
    """
    pass
