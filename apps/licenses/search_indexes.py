"""
Search indexes for the licenses app.
"""

from haystack import indexes

from .models import License


class LicenseIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``License`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """
        Return the model class for this index.
        """
        return License

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.all()

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'
