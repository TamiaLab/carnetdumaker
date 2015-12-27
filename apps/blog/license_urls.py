"""
URLCONF for the blog app (add-on urls for the license app).
"""

from django.conf.urls import url

from . import views, feeds


# URL patterns configuration
urlpatterns = (

    # License index page
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/articles/$', views.license_detail, name='license_articles_detail'),

    # Related articles feed
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/articles/flux/$', feeds.LatestArticlesForLicenseFeed(),
        name='latest_license_articles_rss'),
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/articles/flux/atom/$', feeds.LatestArticlesForLicenseAtomFeed(),
        name='latest_license_articles_atom'),
)
