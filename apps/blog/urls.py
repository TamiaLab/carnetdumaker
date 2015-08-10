"""
URLCONF for the blog app.
"""

from django.conf.urls import url

from . import views, feeds


# URL patterns configuration
urlpatterns = (

    # Blog index page
    url(r'^$', views.article_list, name='index'),

    # Latest articles feed
    url(r'^flux/$', feeds.LatestArticlesFeed(), name='latest_articles_rss'),
    url(r'^flux/atom/$', feeds.LatestArticlesAtomFeed(), name='latest_articles_atom'),

    # Article tag index view
    url(r'^tags/$', views.tag_list, name='tag_list'),

    # Article tag view
    url(r'^tags/(?P<slug>[-a-zA-Z0-9_]+)/$', views.tag_detail, name='tag_detail'),

    # Latest articles for a specific tag feed
    url(r'^/tags/(?P<slug>[-a-zA-Z0-9_]+)/flux/$', feeds.LatestArticlesForTagFeed(),
        name='latest_tag_articles_rss'),
    url(r'^/tags/(?P<slug>[-a-zA-Z0-9_]+)/flux/atom/$', feeds.LatestArticlesForTagAtomFeed(),
        name='latest_tag_articles_atom'),

    # Article category index view
    url(r'^categories/$', views.category_list, name='category_list'),

    # Article category view
    url(r'^categories/(?P<hierarchy>[-a-zA-Z0-9_/]+)/$', views.category_detail, name='category_detail'),

    # Latest articles for a specific category feed
    url(r'^/categories/(?P<hierarchy>[-a-zA-Z0-9_/]+)/flux/$', feeds.LatestArticlesForCategoryFeed(),
        name='latest_category_articles_rss'),
    url(r'^/categories/(?P<hierarchy>[-a-zA-Z0-9_/]+)/flux/atom/$', feeds.LatestArticlesForCategoryAtomFeed(),
        name='latest_category_articles_atom'),

    # Article archives views
    url(r'^archives/$', views.archive_index, name='archive_index'),
    url(r'^archives/(?P<year>[0-9]{4})/$', views.archive_year, name='archive_year'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.archive_month, name='archive_month'),

    # Archives feed
    url(r'^/archives/(?P<year>[0-9]{4})/flux/$', feeds.ArticlesForYearFeed(),
        name='articles_archive_year_rss'),
    url(r'^/archives/(?P<year>[0-9]{4})/flux/atom/$', feeds.ArticlesForYearAtomFeed(),
        name='articles_archive_year_atom'),
    url(r'^/archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/flux/$', feeds.ArticlesForYearAndMonthFeed(),
        name='articles_archive_month_rss'),
    url(r'^/archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/flux/atom/$', feeds.ArticlesForYearAndMonthAtomFeed(),
        name='articles_archive_month_atom'),

    # Article detail views
    url(r'^(?P<year>[0-9]{4})/(?P<slug>[-a-zA-Z0-9_]+)/$',
        views.article_detail_year_month_day, name='article_detail_year'),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<slug>[-a-zA-Z0-9_]+)/$',
        views.article_detail_year_month_day, name='article_detail_year_month'),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[-a-zA-Z0-9_]+)/$',
        views.article_detail_year_month_day, name='article_detail_year_month_day'),
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/$', views.article_detail, name='article_detail'),
)
