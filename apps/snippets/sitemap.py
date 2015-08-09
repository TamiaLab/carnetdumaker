"""
Sitemap for the code snippets app.
"""

from django.contrib.sitemaps import Sitemap

from .models import CodeSnippet


class CodeSnippetsSitemap(Sitemap):
    """
    Sitemap for the code snippets.
    """

    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        """
        Return all public code snippets.
        :return: All public code snippets.
        """
        return CodeSnippet.objects.public_snippets()

    def lastmod(self, obj):
        """
        Return the last modification date of the given code snippet.
        :param obj: The code snippet.
        :return: The last modification date of the given code snippet.
        """
        return obj.last_modification_date or obj.creation_date
