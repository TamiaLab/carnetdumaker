"""
RSS/Atom feeds for the blog app.
"""

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from apps.licenses.models import License

from .models import (Article,
                     ArticleTag,
                     ArticleCategory)
from .settings import NB_ARTICLES_PER_FEED


class BaseBlogArticleFeed(Feed):
    """
    Base feed for articles.
    """

    def items(self):
        """
        Require implementation.
        """
        raise NotImplementedError()

    def item_title(self, item):
        """
        Return the title of the article.
        :param item: The current feed item.
        """
        return item.title

    def item_description(self, item):
        """
        Return the description of the article.
        :param item: The current feed item.
        """
        content_html = item.content_html  # TODO handle membership restriction
        # FIXME Handle footnotes
        return '<p><strong>%s</strong></p>\n%s' % (item.description_html, content_html) if item.description_html else content_html

    def item_author_name(self, item):
        """
        Return the author name for the article.
        :param item: The current feed item.
        """
        return item.author.username if item.author.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the published date of the article.
        :param item: The current feed item.
        """
        return item.pub_date

    def item_updateddate(self, item):
        """
        Return the last modification date of the article.
        :param item: The current feed item.
        """
        return item.last_content_modification_date or item.pub_date

    def item_categories(self, item):
        """
        Return the list of categories of the article.
        :param item: The current feed item.
        """
        cat_names = [c.name for c in item.categories.all()]
        tag_names = [t.name for t in item.tags.all()]
        return cat_names + tag_names


class LatestArticlesFeed(BaseBlogArticleFeed):
    """
    Feed of latest articles.
    """

    title = _('Latest articles')
    link = reverse_lazy('blog:index')
    feed_url = reverse_lazy('blog:latest_articles_rss')
    description = _('Latest articles, all categories together')

    def items(self):
        """
        Return a list of the N most recent articles.
        """
        return Article.objects.published().select_related('author') \
                   .prefetch_related('categories', 'tags')[:NB_ARTICLES_PER_FEED]


class LatestArticlesAtomFeed(LatestArticlesFeed):
    """
    Feed of latest articles (ATOM version).
    """

    feed_type = Atom1Feed
    feed_url = reverse_lazy('blog:latest_articles_atom')
    subtitle = LatestArticlesFeed.description


class LatestArticlesForCategoryFeed(BaseBlogArticleFeed):
    """
    Feed of latest articles for a specific category.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Return the desired ArticleCategory object by his slug hierarchy.
        :param request: The current request.
        :param args: Extra arguments.
        :param kwargs: Extra keywords arguments.
        :return: ArticleCategory
        """

        # Get desired category hierarchy
        hierarchy = kwargs.pop('hierarchy')
        assert hierarchy is not None

        # Get the category object by slug hierarchy
        return ArticleCategory.objects.get(slug_hierarchy=hierarchy)

    def title(self, obj):
        """
        Return the title of the category.
        :param obj: The feed object.
        """
        return _('Latest articles in category "%s"') % obj.name

    def link(self, obj):
        """
        Return the permalink to the category.
        :param obj: The feed object.
        """
        return obj.get_absolute_url()

    def feed_url(self, obj):
        """
        Return the permalink to the latest articles RSS feed for this category.
        :param obj: The feed object.
        """
        return obj.get_latest_articles_rss_feed_url()

    def description(self, obj):
        """
        Return the description of the category.
        :param obj: The feed object.
        """
        return obj.description or _('Latest articles in category "%s"') % obj.name

    def items(self, obj):
        """
        Return all article for this category.
        :param obj: The feed object.
        """
        return obj.articles.published().select_related('author') \
                   .prefetch_related('categories', 'tags')[:NB_ARTICLES_PER_FEED]


class LatestArticlesForCategoryAtomFeed(LatestArticlesForCategoryFeed):
    """
    Feed of latest articles for a specific category (ATOM version).
    """

    feed_type = Atom1Feed
    subtitle = LatestArticlesForCategoryFeed.description

    def feed_url(self, obj):
        """
        Return the permalink to the latest articles ATOM feed for this category.
        :param obj: The feed object.
        """
        return obj.get_latest_articles_atom_feed_url()


class LatestArticlesForLicenseFeed(BaseBlogArticleFeed):
    """
    Feed of latest articles for a specific license.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Return the desired License object by his slug.
        :param request: The current request.
        :param args: Extra arguments.
        :param kwargs: Extra keywords arguments.
        :return: ArticleLicense
        """

        # Get desired license slug
        slug = kwargs.pop('slug')
        assert slug is not None

        # Retrieve the license object
        return License.objects.get(slug=slug)

    def title(self, obj):
        """
        Return the title of the license.
        :param obj: The feed object.
        """
        return _('Latest articles with license "%s"') % obj.name

    def link(self, obj):
        """
        Return the permalink to the license.
        :param obj: The feed object.
        """
        return obj.get_absolute_url()

    def description(self, obj):
        """
        Return the description of the license.
        :param obj: The feed object.
        """
        return obj.description_html or _('Latest articles with license "%s"') % obj.name

    # TODO def feed_url(self, obj):

    def items(self, obj):
        """
        Return all article for this license.
        :param obj: The feed object.
        """
        return obj.articles.published().select_related('author') \
                   .prefetch_related('categories', 'tags')[:NB_ARTICLES_PER_FEED]


class LatestArticlesForLicenseAtomFeed(LatestArticlesForLicenseFeed):
    """
    Feed of latest articles for a specific license (ATOM version).
    """

    feed_type = Atom1Feed
    subtitle = LatestArticlesForLicenseFeed.description

    # TODO def feed_url(self, obj):


class LatestArticlesForTagFeed(BaseBlogArticleFeed):
    """
    Feed of latest articles for a specific tag.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Return the desired ArticleTag object by his slug.
        :param request: The current request.
        :param args: Extra arguments.
        :param kwargs: Extra keywords arguments.
        :return: ArticleTag
        """

        # Get desired tag slug
        slug = kwargs.pop('slug')
        assert slug is not None

        # Retrieve the tag object
        return ArticleTag.objects.get(slug=slug)

    def title(self, obj):
        """
        Return the title of the tag.
        :param obj: The feed object.
        """
        return _('Latest articles with tag "%s"') % obj.name

    def link(self, obj):
        """
        Return the permalink to the tag.
        :param obj: The feed object.
        """
        return obj.get_absolute_url()

    def description(self, obj):
        """
        Return the description of the tag.
        :param obj: The feed object.
        """
        return _('Latest articles with tag "%s"') % obj.name

    def feed_url(self, obj):
        """
        Return the permalink to the latest articles RSS feed for this tag.
        :param obj: The feed object.
        """
        return obj.get_latest_articles_rss_feed_url()

    def items(self, obj):
        """
        Return all article for this tag.
        :param obj: The feed object.
        """
        return obj.articles.published().select_related('author') \
                   .prefetch_related('categories', 'tags')[:NB_ARTICLES_PER_FEED]


class LatestArticlesForTagAtomFeed(LatestArticlesForTagFeed):
    """
    Feed of latest articles for a specific tag (ATOM version).
    """

    feed_type = Atom1Feed
    subtitle = LatestArticlesForTagFeed.description

    def feed_url(self, obj):
        """
        Return the permalink to the latest articles Atom feed for this tag.
        :param obj: The feed object.
        """
        return obj.get_latest_articles_atom_feed_url()


class ArticlesForYearFeed(BaseBlogArticleFeed):
    """
    Feed of articles for a specific year.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Return the desired year as a dict.
        :param request: The current request.
        :param args: Extra arguments.
        :param kwargs: Extra keywords arguments.
        :return: dict with year key.
        """

        # Get desired archive year
        year = kwargs.pop('year')
        assert year is not None

        # Return the year
        return {'year': year}

    def title(self, obj):
        """
        Return the title of the archive.
        :param obj: The feed object.
        """
        return _('Latest articles for year %(year)s') % obj

    def link(self, obj):
        """
        Return the permalink to the archive.
        :param obj: The feed object.
        """
        return reverse_lazy('blog:archive_year', kwargs=obj)

    def description(self, obj):
        """
        Return the description of the archive.
        :param obj: The feed object.
        """
        return _('Latest articles for year %(year)s') % obj

    def feed_url(self, obj):
        """
        Return the permalink to the articles archive RSS feed for this year.
        :param obj: The feed object.
        """
        return reverse_lazy('blog:articles_archive_year_rss', kwargs=obj)

    def items(self, obj):
        """
        Return all article for this archive.
        :param obj: The feed object.
        """
        return Article.objects.published().filter(pub_date__year=int(obj['year'])) \
            .select_related('author').prefetch_related('categories', 'tags')


class ArticlesForYearAtomFeed(ArticlesForYearFeed):
    """
    Feed of articles for a specific year (ATOM version).
    """

    feed_type = Atom1Feed
    subtitle = ArticlesForYearFeed.description

    def feed_url(self, obj):
        """
        Return the permalink to the articles archive Atom feed for this year.
        :param obj: The feed object.
        """
        return reverse_lazy('blog:articles_archive_year_atom', kwargs=obj)


class ArticlesForYearAndMonthFeed(BaseBlogArticleFeed):
    """
    Feed of articles for a specific year and month.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Return the desired year and month as a dict.
        :param request: The current request.
        :param args: Extra arguments.
        :param kwargs: Extra keywords arguments.
        :return: dict with year and month keys.
        """

        # Get desired archive year and month
        year = kwargs.pop('year')
        month = kwargs.pop('month')
        assert year is not None
        assert month is not None

        # Return the year and month
        return {'year': year, 'month': month}

    def title(self, obj):
        """
        Return the title of the archive.
        :param obj: The feed object.
        """
        return _('Latest articles for month %(year)s/%(month)s') % obj

    def link(self, obj):
        """
        Return the permalink to the archive.
        :param obj: The feed object.
        """
        return reverse_lazy('blog:archive_month', kwargs=obj)

    def description(self, obj):
        """
        Return the description of the archive.
        :param obj: The feed object.
        """
        return _('Latest articles for month %(year)s/%(month)s') % obj

    def feed_url(self, obj):
        """
        Return the permalink to the articles archive RSS feed for this year.
        :param obj: The feed object.
        """
        return reverse_lazy('blog:articles_archive_month_rss', kwargs=obj)

    def items(self, obj):
        """
        Return all article for this archive.
        :param obj: The feed object.
        """
        return Article.objects.published().filter(pub_date__year=int(obj['year']),
                                                  pub_date__month=int(obj['month'])) \
            .select_related('author').prefetch_related('categories', 'tags')


class ArticlesForYearAndMonthAtomFeed(ArticlesForYearAndMonthFeed):
    """
    Feed of articles for a specific year and month (ATOM version).
    """

    feed_type = Atom1Feed
    subtitle = ArticlesForYearAndMonthFeed.description

    def feed_url(self, obj):
        """
        Return the permalink to the articles archive Atom feed for this year.
        :param obj: The feed object.
        """
        return reverse_lazy('blog:articles_archive_month_atom', kwargs=obj)
