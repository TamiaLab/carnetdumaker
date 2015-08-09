"""
Sitemap for the blog app.
"""

from django.contrib.sitemaps import Sitemap

from .models import (Article,
                     ArticleTag,
                     ArticleCategory)


class ArticlesSitemap(Sitemap):
    """
    Sitemap for the blog's articles.
    """

    changefreq = 'daily'
    priority = 0.5

    def items(self):
        """
        Return all the published articles.
        :return: All the published articles.
        """
        return Article.objects.published()

    def lastmod(self, obj):
        """
        Return the last modification date of the given article.
        :param obj: The article.
        :return: The last modification date of the given article.
        """
        return obj.last_content_modification_date or obj.pub_date


class ArticleTagsSitemap(Sitemap):
    """
    Sitemap for the blog's article tags.
    """

    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        """
        Return all article tags.
        :return: All article tags.
        """
        return ArticleTag.objects.all()


class ArticleCategoriesSitemap(Sitemap):
    """
    Sitemap for the blog's article categories.
    """

    changefreq = 'weekly'
    priority = 0.3

    def items(self):
        """
        Return all article categories.
        :return: All article categories.
        """
        return ArticleCategory.objects.all()
