"""
URLCONF for the announcements app.
"""

from django.conf.urls import url

from . import views, feeds


# URL patterns configuration
urlpatterns = (

    # Announcements index page
    url(r'^$', views.announcement_list, name='index'),

    # Recent announcements feeds
    url(r'^flux/$', feeds.LatestAnnouncementsFeed(), name='latest_announcements_rss'),
    url(r'^flux/atom/$', feeds.LatestAnnouncementsAtomFeed(), name='latest_announcements_atom'),

    # Tags list view
    url(r'^tags/$', views.tag_list, name='tag_list'),

    # Tag detail view
    url(r'^tags/(?P<slug>[-a-zA-Z0-9_]+)/$', views.tag_detail, name='tag_detail'),

    # Recent announcements feeds for a specific tag
    url(r'^tags/(?P<slug>[-a-zA-Z0-9_]+)/flux/$', feeds.LatestAnnouncementsForTagFeed(),
        name='latest_tag_announcements_rss'),
    url(r'^tags/(?P<slug>[-a-zA-Z0-9_]+)/flux/atom/$', feeds.LatestAnnouncementsForTagAtomFeed(),
        name='latest_tag_announcements_atom'),

    # Announcements index page
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/$', views.announcement_detail, name='announcement_detail'),
)
