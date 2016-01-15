"""
Search indexes for the snippets app.
"""

from haystack import indexes

from .models import CodeSnippet


class CodeSnippetIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``CodeSnippet`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    license = indexes.CharField(model_attr='license', null=True)

    def get_model(self):
        """
        Return the model class for this index.
        """
        return CodeSnippet

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
