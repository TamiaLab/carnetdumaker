"""
URLCONF for the code snippets app.
"""

from django.conf.urls import url

from . import views, feeds


# URL patterns configuration
urlpatterns = (

    # Snippets list view
    url(r'^$', views.snippet_list, name='index'),

    # RSS and ATOM feeds
    url(r'^flux/$', feeds.LatestCodeSnippetsFeed(), name='latest_snippets_rss'),
    url(r'^flux/atom/$', feeds.LatestCodeSnippetsAtomFeed(), name='latest_snippets_atom'),

    # Snippet detail page
    url(r'^(?P<pk>[0-9]+)/$', views.snippet_detail, name='snippet_detail'),

    # Snippet raw content page
    url(r'^(?P<pk>[0-9]+)/source/$', views.snippet_raw, name='snippet_raw'),

    # Snippet download page
    url(r'^(?P<pk>[0-9]+)/telechargement/$', views.snippet_raw, {'download': True}, name='snippet_download'),

    # Snippet download in zip page
    url(r'^(?P<pk>[0-9]+)/telechargement-zip/$', views.snippet_zip_download, name='snippet_zip_download'),

    # Snippets bundle list view
    url(r'^dossiers/$', views.bundle_list, name='bundle_index'),

    # Snippets detail view
    url(r'^dossiers/(?P<pk>[0-9]+)/$', views.bundle_detail, name='bundle_detail'),

    # Snippet download page
    url(r'^dossiers/(?P<pk>[0-9]+)/telechargement/$', views.bundle_download, name='bundle_download'),
)
