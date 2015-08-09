"""
Data models for the file attachments app.
"""

import uuid
import mimetypes

import os
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .settings import FILE_ATTACHMENTS_UPLOAD_DIR_NAME
from .managers import FileAttachmentManager


def _upload_to_file_attachment(instance, filename):
    """
    ``upload_to`` path generator for the attachment files.
    :param instance: The ``FileAttachment`` instance.
    :param filename: The current filename.
    :return: The file attachment filename with path like "FILE_ATTACHMENTS_UPLOAD_DIR_NAME/%(uuid)s".
    """

    # Store mime-type and filename
    mimetype = mimetypes.guess_type(filename)
    instance.mimetype = mimetype[0] if mimetype is not None else 'application/octet-stream'
    instance.filename = filename

    # Return the new filename with path
    return os.path.join(FILE_ATTACHMENTS_UPLOAD_DIR_NAME, str(uuid.uuid4().hex))


class FileAttachment(models.Model):
    """
    File attachment data model.
    A file attachment is made of:
    - a parent post,
    - a file,
    - a file size (for display),
    - the original filename (because each file are renamed with an uuid4 to avoid security problems),
    - an upload date.
    """

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    file = models.FileField(_('File'),
                            upload_to=_upload_to_file_attachment)

    size = models.IntegerField(_('File size'))

    # MUST be AFTER ``file``, because pre_save generate SQL in declaration order and the
    # upload_to callable set the filename attribute to store the original uploaded filename.
    filename = models.CharField(_('Original filename'),
                                max_length=1024,
                                blank=True)

    # MUST be AFTER ``file``, because pre_save generate SQL in declaration order and the
    # upload_to callable set the content_type attribute.
    mimetype = models.CharField(_('Content type'),
                                    max_length=255)

    upload_date = models.DateTimeField(_('Upload date'),
                                       auto_now_add=True)

    objects = FileAttachmentManager()

    class Meta(object):
        verbose_name = _('File attachment')
        verbose_name_plural = _('File attachments')
        get_latest_by = 'upload_date'
        ordering = ('-upload_date', 'filename')

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        """
        Save the model.
        :param args: for super()
        :param kwargs: for super()
        """

        # Store the file's size in bytes
        self.size = self.file.size

        # Save the model
        super(FileAttachment, self).save(*args, **kwargs)

    def get_size_display(self):
        """
        Get the size as string for display.
        """
        size = self.size
        if not size:
            return ''
        if size < 1024:
            return _('%dB') % size
        elif size < 1024 * 1024:
            return _('%dKB') % int(size / 1024)
        else:
            return _('%.2fMB') % (size / float(1024 * 1024))
    get_size_display.short_description = _('File size')
    get_size_display.admin_order_field = 'size'

    def get_absolute_url(self):
        """
        Return the permalink to this attachment.
        """
        return reverse('fileattachments:attachment_download', kwargs={'pk': self.pk})
