"""
Search indexes for the bug tracker app.
"""

from haystack import indexes

from .models import (IssueTicket,
                     IssueComment)


class IssueTicketIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``IssueTicket`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    component = indexes.CharField(model_attr='component', null=True)

    submitter = indexes.CharField(model_attr='submitter')

    submission_date = indexes.DateTimeField(model_attr='submission_date')

    assigned_to = indexes.CharField(model_attr='assigned_to', null=True)

    status = indexes.CharField(model_attr='status')

    priority = indexes.CharField(model_attr='priority')

    difficulty = indexes.CharField(model_attr='difficulty')

    def get_model(self):
        """
        Return the model class for this index.
        """
        return IssueTicket

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.all() \
            .select_related('component', 'submitter', 'assigned_to')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'


class IssueCommentIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``IssueComment`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    author = indexes.CharField(model_attr='author')

    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        """
        Return the model class for this index.
        """
        return IssueComment

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.all().select_related('issue', 'author')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'
