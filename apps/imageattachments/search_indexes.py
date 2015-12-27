"""
Search indexes for the image attachments app.
"""

from haystack import indexes

from .models import ImageAttachment


class ImageAttachmentIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``ImageAttachment`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    license = indexes.CharField(model_attr='license')

    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        """
        Return the model class for this index.
        """
        return ImageAttachment

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.published().select_related('license')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'
