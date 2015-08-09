"""
Forms for the file attachments app.
"""

import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.multiupload.fields import MultiFileField

from .models import FileAttachment
from .settings import (FILE_ATTACHMENTS_MAX_FILE_COUNT,
                       FILE_ATTACHMENTS_MAX_FILE_SIZE,
                       FILE_ATTACHMENTS_MAX_TOTAL_SIZE)


ATTACHMENT_FIELD_RE = re.compile(r'^attachment_([0-9]+)$')
# TODO change to POSt list (with POST.getlist('attachment'))


class NewAttachmentsMixin(object):
    """
    Form mixin for adding new attachments to a model.
    """

    def __init__(self, *args, **kwargs):
        super(NewAttachmentsMixin, self).__init__(*args, **kwargs)
        self.fields['attachments'] = MultiFileField(label=_('File attachments'),
                                                    min_num=0,
                                                    max_num=FILE_ATTACHMENTS_MAX_FILE_COUNT,
                                                    max_file_size=FILE_ATTACHMENTS_MAX_FILE_SIZE,
                                                    max_total_file_size=FILE_ATTACHMENTS_MAX_TOTAL_SIZE,
                                                    required=False)

    def handle_new_attachments(self, parent_object):
        """
        Handle new attachments creation. To be called in Form.save() method.
        :param parent_object: The parent object instance.
        """

        # Handle new attachments
        for attachment in self.cleaned_data['attachments']:
            FileAttachment.objects.create(content_object=parent_object, file=attachment)


class EditAttachmentsMixin(NewAttachmentsMixin):
    """
    Form mixin for adding new attachments to a model instance with an ``attachments`` attribute
    of type ``GenericRelation`` and editing current attachments.
    """

    def do_clean_attachments(self, parent_object):
        """
        Check if old attachments + new attachments don't fuck with limits.
        To be called in Form.clean() method.
        :param parent_object: The parent object instance.
        """
        if 'attachments' not in self.cleaned_data:
            # Avoid cleaning attachments if the field is not valid
            return
        attachments = self.cleaned_data['attachments']
        old_attachments_size = parent_object.attachments.get_total_size(exclude=self.get_deleted_attachment_ids())
        new_attachments_size = sum(a.size for a in attachments)
        if old_attachments_size + new_attachments_size > FILE_ATTACHMENTS_MAX_TOTAL_SIZE:
            raise forms.ValidationError(_('Total files size exceed maximum upload size %(total_max_size)s bytes.'),
                                        code='total_file_size', params={'total_max_size':
                                                                            FILE_ATTACHMENTS_MAX_TOTAL_SIZE})
        return attachments

    def add_attachment_fields(self, parent_object):
        """
        Add fields for all current attachments of the parent object. To be called in Form.__init__() method,
        after super().
        :param parent_object: The parent object instance.
        """

        # Add all attachment fields
        for attachment in parent_object.attachments.all():
            self.fields['attachment_%d' % attachment.id] = \
                forms.BooleanField(label=_('%s (untick to delete)') % attachment.filename,
                                   initial=True,
                                   required=False)

    def get_deleted_attachment_ids(self):
        """
        Return a list of IDs of all deleted attachments.
        """
        ids = []
        for name, value in self.cleaned_data.items():
            match = ATTACHMENT_FIELD_RE.match(name)
            if match and not value:
                ids.append(match.group(1))
        return ids

    def handle_deleted_attachments(self, parent_object):
        """
        Handle deleted attachments deletion. To be called in Form.save() method.
        :param parent_object: The parent object instance.
        """

        # Handle deleted attachments
        FileAttachment.objects.filter(content_object=parent_object,
                                      id__in=self.get_deleted_attachment_ids()).delete()
