"""
Search indexes for the forum app.
"""

from haystack import indexes

from .models import (Forum,
                     ForumThread,
                     ForumThreadPost)


class ForumIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``Forum`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    closed = indexes.BooleanField(model_attr='closed')

    def get_model(self):
        """
        Return the model class for this index.
        """
        return Forum

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.all().select_related('category')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'


class ForumThreadIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``ForumThread`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    closed = indexes.BooleanField(model_attr='closed')

    resolved = indexes.BooleanField(model_attr='resolved')

    def get_model(self):
        """
        Return the model class for this index.
        """
        return ForumThread

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.public_threads().select_related('parent_forum',
                                                                        'first_post__author',
                                                                        'last_post__author')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'


class ForumThreadPostIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``ForumThreadPost`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    author = indexes.CharField(model_attr='author')

    pub_date = indexes.DateTimeField(model_attr='pub_date')

    last_content_modification_date = indexes.DateTimeField(model_attr='last_content_modification_date', null=True)

    def get_model(self):
        """
        Return the model class for this index.
        """
        return ForumThreadPost

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.public_published() \
            .select_related('parent_thread',
                            'author',
                            'last_modification_by').prefetch_related('attachments')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'
