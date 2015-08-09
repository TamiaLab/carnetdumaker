"""
Data models managers for the file attachments app.
"""

from django.db import models


class FileAttachmentManager(models.Manager):
    """
    Manager class for the ``FileAttachment`` data model.
    """

    use_for_related_fields = True

    def get_total_size(self, exclude=None):
        """
        Return the sum of all attachment's sizes.
        :param exclude: List of excluded attachment's ids.
        """
        if exclude is not None:
            queryset = self.exclude(id__in=exclude)
        else:
            queryset = self.all()
        result = queryset.aggregate(models.Sum('size'))['size__sum']
        return result if result is not None else 0
