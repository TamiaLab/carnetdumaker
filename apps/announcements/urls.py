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

    # Announcements index page
    url(r'^(?P<slug>[-a-zA-Z0-9_]+)/$', views.announcement_detail, name='announcement_detail'),
)
