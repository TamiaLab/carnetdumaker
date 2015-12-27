"""
Search indexes for the announcements app.
"""

from haystack import indexes

from .models import Announcement


class AnnouncementIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``Announcement`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    author = indexes.CharField(model_attr='author')

    pub_date = indexes.DateTimeField(model_attr='pub_date')

    last_content_modification_date = indexes.DateTimeField(model_attr='last_content_modification_date', null=True)

    def get_model(self):
        """
        Return the model class for this index.
        """
        return Announcement

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.published().select_related('author').prefetch_related('tags')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'
