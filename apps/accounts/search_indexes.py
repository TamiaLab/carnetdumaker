"""
Search indexes for the user accounts app.
"""

from haystack import indexes

from .models import UserProfile


class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Search indexes for the ``UserProfile`` model.
    """

    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """
        Return the model class for this index.
        """
        return UserProfile

    def index_queryset(self, using=None):
        """
        Used when the entire index for this model is updated.
        """
        return self.get_model().objects.get_active_users_accounts().select_related('user')

    def get_updated_field(self):
        """
        Return the field name used to filter out recently modified objects.
        """
        return 'last_modification_date'
