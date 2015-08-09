"""
URLCONF for the forum app.
"""

from django.conf.urls import url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from apps.contentreport.views import report_content

from . import views, feeds
from .models import ForumThreadPost
from .forms import ForumThreadPostReportForm


# URL patterns configuration
urlpatterns = (

    # Forum index page
    url(r'^$', views.forum_index, name='index'),
    url(r'^topics/$', RedirectView.as_view(url=reverse_lazy('forum:index'), permanent=True)),
    url(r'^posts/$', RedirectView.as_view(url=reverse_lazy('forum:index'), permanent=True)),

    # Forum's thread detail view
    url(r'^topics/(?P<pk>[0-9]+)-(?P<slug>[\w-]+)/$', views.forum_thread_show, name='thread_detail'),

    # Forum's thread edit view
    url(r'^topics/(?P<pk>[0-9]+)-(?P<slug>[\w-]+)/modifier/$', views.forum_thread_edit, name='thread_edit'),

    # Forum's thread delete view
    url(r'^topics/(?P<pk>[0-9]+)-(?P<slug>[\w-]+)/supprimer/$', views.forum_thread_delete, name='thread_delete'),

    # Forum's thread delete view
    url(r'^topics/(?P<pk>[0-9]+)-(?P<slug>[\w-]+)/repondre/$', views.forum_thread_reply, name='thread_reply'),

    # Issue ticket subscription management
    url(r'^topics/(?P<pk>[0-9]+)-(?P<slug>[\w-]+)/abonner/$', views.topic_subscribe, name='thread_subscribe'),
    url(r'^topics/(?P<pk>[0-9]+)-(?P<slug>[\w-]+)/desabonner/$', views.topic_unsubscribe, name='thread_unsubscribe'),

    # Latest forum's threads feeds
    url(r'^topics/flux/$', feeds.LatestForumThreadsFeed(),
        name='latest_forum_threads_rss'),
    url(r'^topics/flux/atom/$', feeds.LatestForumThreadsAtomFeed(),
        name='latest_forum_threads_atom'),

    # Latest forum's thread's posts for a given thread feeds
    url(r'^topics/(?P<pk>\d+)-(?P<slug>[\w-]+)/flux/$', feeds.LatestForumPostsForThreadFeed(),
        name='latest_forum_thread_posts_for_thread_rss'),
    url(r'^topics/(?P<pk>\d+)-(?P<slug>[\w-]+)/flux/atom/$', feeds.LatestForumPostsForThreadAtomFeed(),
        name='latest_forum_thread_posts_for_thread_atom'),

    # Forum's thread's post detail view (redirect to thread view)
    url(r'^posts/(?P<pk>[0-9]+)/$', views.forum_thread_post_show, name='post_detail'),

    # Forum's thread's post edit view
    url(r'^posts/(?P<pk>[0-9]+)/modifier/$', views.forum_thread_post_edit, name='post_edit'),

    # Forum's thread's post delete view
    url(r'^posts/(?P<pk>[0-9]+)/supprimer/$', views.forum_thread_post_delete, name='post_delete'),

    # Forum's thread's post reply (with quote) view
    url(r'^posts/(?P<pk>[0-9]+)/repondre/$', views.forum_thread_post_reply, name='post_reply'),

    # Forum's thread's post report view
    url(r'^posts/(?P<pk>[0-9]+)/signaler/$', report_content, kwargs={
        'objects_loader': ForumThreadPost.objects.published().select_related('parent_thread',
                                                                             'parent_thread__parent_forum',
                                                                             'author'),
        'content_object_name': 'post',
        'template_name': 'forum/forum_thread_post_report.html',
        'content_report_form': ForumThreadPostReportForm,
    }, name='post_report'),

    # Latest forum's thread's posts feeds
    url(r'^posts/flux/$', feeds.LatestForumPostsFeed(),
        name='latest_forum_thread_posts_rss'),
    url(r'^posts/flux/atom/$', feeds.LatestForumPostsAtomFeed(),
        name='latest_forum_thread_posts_atom'),

    # My account view
    url(r'^mon-compte/$', views.my_account_show, name='myaccount'),

    # My threads and posts list view
    url(r'^mon-compte/mes-topics/$', views.my_threads_list, name='mythreads_list'),
    url(r'^mon-compte/mes-posts/$', views.my_posts_list, name='myposts_list'),

    # My forum's subscriptions list view
    url(r'^mon-compte/mes-abonnements-forums/$', views.my_forums_subscription_list, name='myforumsubscribtions_list'),
    url(r'^mon-compte/mes-abonnements-topics/$', views.my_threads_subscription_list, name='mythreadsubscribtions_list'),

    # Forum's thread create view
    url(r'^(?P<hierarchy>[\w/-]+)/nouveau-topic/$', views.forum_thread_create, name='thread_create'),

    # Issue ticket subscription management
    url(r'^(?P<hierarchy>[\w/-]+)/abonner/$', views.forum_subscribe, name='forum_subscribe'),
    url(r'^(?P<hierarchy>[\w/-]+)/desabonner/$', views.forum_unsubscribe, name='forum_unsubscribe'),

    # Latest forum's threads for a given forum feeds
    url(r'^(?P<hierarchy>[\w/-]+)/flux-topics/$', feeds.LatestForumThreadsForForumFeed(),
        name='latest_forum_threads_for_forum_rss'),
    url(r'^(?P<hierarchy>[\w/-]+)/flux-topics/atom/$', feeds.LatestForumThreadsForForumAtomFeed(),
        name='latest_forum_threads_for_forum_atom'),

    # Latest forum's thread's posts for a given forum feeds
    url(r'^(?P<hierarchy>[\w/-]+)/flux-posts/$', feeds.LatestForumPostsForForumFeed(),
        name='latest_forum_thread_posts_for_forum_rss'),
    url(r'^(?P<hierarchy>[\w/-]+)/flux-posts/atom/$', feeds.LatestForumPostsForForumAtomFeed(),
        name='latest_forum_thread_posts_for_forum_atom'),

    # Mark all threads of the forum as read confirm view
    url(r'^(?P<hierarchy>[\w/-]+)/menage/$', views.forum_mark_all_thread_as_read,
        name='forum_mark_all_threads_as_read'),

    # Sub-forum detail view
    # NOTE: Always last URL because regex match nearly every possible urls.
    url(r'^(?P<hierarchy>[\w/-]+)/$', views.forum_show, name='forum_detail'),
)
