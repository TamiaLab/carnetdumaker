"""
URLCONF for the blog app.
"""

from django.conf.urls import url

from . import views, feeds


# URL patterns configuration
urlpatterns = (

    # License index page
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/$', views.license_detail, name='license_detail'),

    # Related articles feed
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/flux/$', feeds.LatestArticlesFeed(), name='latest_license_articles_rss'),
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/flux/atom/$', feeds.LatestArticlesAtomFeed(), name='latest_license_articles_atom'),
)
