"""
HTML5 multiple files upload form field.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class MultiFileInput(forms.FileInput):
    """
    HTML5 multiple files upload form field.
    """

    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return [files.get(name)]


class MultiFileField(forms.FileField):
    """
    HTML5 multiple files upload form field.
    """

    widget = MultiFileInput

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        self.maximum_total_file_size = kwargs.pop('max_total_file_size', None)
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            i = super(MultiFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret

    def validate(self, data):
        super(MultiFileField, self).validate(data)

        num_files = len(data)
        if len(data) and not data[0]:
            num_files = 0

        if num_files < self.min_num:
            raise ValidationError(_('Ensure that at least %(min_num)s files are uploaded (received %(num_files)s).'),
                                  code='min_num', params={'min_num': self.min_num, 'num_files': num_files})
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(_('Ensure that at most %(max_num)s files are uploaded (received %(num_files)s).'),
                                  code='max_num', params={'max_num': self.max_num, 'num_files': num_files})

        total_files_size = 0
        for uploaded_file in data:
            total_files_size += uploaded_file.size
            if self.maximum_file_size and uploaded_file.size > self.maximum_file_size:
                raise ValidationError(_('File "%(uploaded_file_name)s" exceeded maximum upload size %(max_size)s.'),
                                      code='max_file_size', params={'uploaded_file_name': uploaded_file.name,
                                                                'max_size': self._size_display(self.maximum_file_size)})

        if self.maximum_total_file_size and total_files_size > self.maximum_total_file_size:
            raise ValidationError(_('Total files size exceeded maximum upload size %(total_max_size)s.'),
                                  code='max_total_file_size',
                                  params={'total_max_size': self._size_display(self.maximum_total_file_size)})

    @staticmethod
    def _size_display(size):
        if size < 1024:
            return _('%dB') % size
        elif size < 1024 * 1024:
            return _('%dKB') % int(size / 1024)
        else:
            return _('%.2fMB') % (size / float(1024 * 1024))
