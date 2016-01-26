"""
Data models managers for the code snippets app.
"""

from django.db import models


class CodeSnippetManager(models.Manager):
    """
    Manager class for the ``CodeSnippet`` data model.
    """

    def public_snippets(self):
        """
        Return a queryset of all public snippets, for listing.
        """
        return self.filter(public_listing=True)

    def redo_highlighting(self):
        """
        Redo highlighting of all code snippets.
        """
        for snippet in self.all():
            snippet.save(update_fields=('html_for_display', 'css_for_display'), render_description=False)


class CodeSnippetBundleManager(models.Manager):
    """
    Manager class for the ``CodeSnippet`` data model.
    """

    def public_bundles(self):
        """
        Return a queryset of all public snippets bundles, for listing.
        """
        return self.filter(public_listing=True)
