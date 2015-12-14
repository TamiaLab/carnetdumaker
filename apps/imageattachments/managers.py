"""
Objects managers for the image attachments app.
"""

from django.db import models
from django.utils import timezone


class ImageAttachmentManager(models.Manager):
    """
    Manager class for the ``ImageAttachment`` data model.
    """

    use_for_related_fields = True

    def published(self):
        """
        Return a queryset with all currently published image attachments.
        """
        now = timezone.now()
        return self.filter(pub_date__lte=now)

    def published_public(self):
        """
        Return a queryset with all currently published and publicly listed image attachments.
        """
        return self.published().filter(public_listing=True)
