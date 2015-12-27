"""
Search indexes for the blog app.
"""

from haystack import indexes

from .models import (Article,
                     ArticleTag,
                     ArticleCategory)


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``Article`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    author = indexes.CharField(model_attr='author')

    license = indexes.CharField(model_attr='license')

    pub_date = indexes.DateTimeField(model_attr='pub_date')

    last_content_modification_date = indexes.DateTimeField(model_attr='last_content_modification_date')

    def get_model(self):
        """
        Return the model class for this index.
        """
        return Article

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.published() \
            .select_related('author', 'license').prefetch_related('tags', 'categories', 'head_notes', 'foot_notes')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'


class ArticleTagIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``ArticleTag`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """
        Return the model class for this index.
        """
        return ArticleTag

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


class ArticleCategoryIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``ArticleCategory`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """
        Return the model class for this index.
        """
        return ArticleCategory

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
