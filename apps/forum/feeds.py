"""
RSS/Atom feeds for the forum app.
"""

from django.core.urlresolvers import reverse_lazy
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _

from .models import (Forum,
                     ForumThread,
                     ForumThreadPost)
from .settings import (NB_FORUM_THREADS_IN_FEEDS,
                       NB_FORUM_THREAD_POSTS_IN_FEEDS)


class ForumThreadsBaseFeed(Feed):
    """
    Base class for any forum's threads feed.
    """

    def items(self):
        """
        Return a list of forum's threads.
        """
        raise NotImplementedError()

    def item_title(self, item):
        """
        Return the title of the forum's thread.
        """
        return item.title

    def item_description(self, item):
        """
        Return the description of the forum's thread.
        """
        return item.first_post.content_html

    def item_author_name(self, item):
        """
        Return the author name for the forum's thread.
        """
        author = item.first_post.author
        return author.username if author.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the submitted date of the forum's thread.
        """
        return item.first_post.pub_date

    def item_updateddate(self, item):
        """
        Return the last modification date of the forum's thread.
        """
        return item.last_post.last_modification_date


class ForumPostsBaseFeed(Feed):
    """
    Base class for any forum's thread's posts feed.
    """

    def items(self):
        """
        Return a list of forum's thread's post.
        """
        raise NotImplementedError()

    def item_title(self, item):
        """
        Return the title of the forum's thread's post.
        """
        return item.parent_thread.title

    def item_description(self, item):
        """
        Return the description of the forum's thread's post.
        """
        return item.content_html

    def item_author_name(self, item):
        """
        Return the author name for the forum's thread's post.
        """
        author = item.author
        return author.username if author.is_active else _('Anonymous')

    def item_pubdate(self, item):
        """
        Return the submitted date of the forum's thread's post.
        """
        return item.pub_date

    def item_updateddate(self, item):
        """
        Return the last modification date of the forum's thread's post.
        """
        return item.last_modification_date


class LatestForumThreadsFeed(ForumThreadsBaseFeed):
    """
    Feed of latest forum's thread.
    """
    title = _('Latest forum threads')
    link = reverse_lazy('forum:index')
    description = _('Latest forum threads, all forums together')

    def items(self):
        """
        Return a list of the N most recent (public) forum's threads.
        """
        return ForumThread.objects.public_threads().select_related('first_post__author', 'last_post') \
                   .order_by('-first_post__pub_date')[:NB_FORUM_THREADS_IN_FEEDS]


class LatestForumThreadsAtomFeed(LatestForumThreadsFeed):
    """
    Feed of latest forum's thread (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestForumThreadsFeed.description


class LatestForumPostsFeed(ForumPostsBaseFeed):
    """
    Feed of latest forum's thread's posts.
    """
    title = _('Latest forum posts')
    link = reverse_lazy('forum:index')
    description = _('Latest forum posts, all threads together')

    def items(self):
        """
        Return a list of the five most recent (public) forum's thread's post.
        """
        return ForumThreadPost.objects.select_related('parent_thread__last_post',
                                                      'parent_thread__first_post', 'author') \
                   .filter(parent_thread__parent_forum__private=False) \
                   .order_by('-pub_date')[:NB_FORUM_THREAD_POSTS_IN_FEEDS]


class LatestForumPostsAtomFeed(LatestForumPostsFeed):
    """
    Feed of latest forum's thread's posts (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestForumPostsFeed.description


class LatestForumThreadsForForumFeed(ForumThreadsBaseFeed):
    """
    Feed of latest forum's thread for a given forum.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Get the desired forum.
        """

        # Get desired forum PK
        hierarchy = kwargs.pop('hierarchy')
        assert hierarchy is not None

        # Get the forum
        return Forum.objects.get(slug_hierarchy=hierarchy, private=False)

    def title(self, obj):
        """
        Return the title of the forum.
        """
        return _('Latest forum threads in forum %s') % obj.title

    def link(self, obj):
        """
        Return the permalink to the forum.
        """
        return obj.get_absolute_url()

    def description(self, obj):
        """
        Return the description of the forum.
        """
        return obj.description or _('Latest forum threads in forum %s') % obj.title

    def items(self, obj):
        """
        Return a list of the N most recent (public) forum's threads in the given forum.
        """
        return obj.threads.public_threads().select_related('first_post__author', 'last_post') \
                   .order_by('-first_post__pub_date')[:NB_FORUM_THREADS_IN_FEEDS]


class LatestForumThreadsForForumAtomFeed(LatestForumThreadsForForumFeed):
    """
    Feed of latest forum's thread for a given forum (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestForumThreadsForForumFeed.description


class LatestForumPostsForForumFeed(ForumPostsBaseFeed):
    """
    Feed of latest forum's thread's posts for a given forum.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Get the desired forum.
        """

        # Get desired forum PK
        hierarchy = kwargs.pop('hierarchy')
        assert hierarchy is not None

        # Get the forum
        return Forum.objects.get(slug_hierarchy=hierarchy, private=False)

    def title(self, obj):
        """
        Return the title of the forum.
        """
        return _('Latest forum posts in forum %s') % obj.title

    def link(self, obj):
        """
        Return the permalink to the forum.
        """
        return obj.get_absolute_url()

    def description(self, obj):
        """
        Return the description of the forum.
        """
        return obj.description or _('Latest forum posts in forum %s') % obj.title

    def items(self, obj):
        """
        Return a list of the N most recent (public) forum's thread's post in the given forum.
        """
        return ForumThreadPost.objects.select_related('parent_thread__last_post',
                                                      'parent_thread__first_post', 'author') \
                   .filter(parent_thread__parent_forum=obj) \
                   .order_by('-pub_date')[:NB_FORUM_THREAD_POSTS_IN_FEEDS]


class LatestForumPostsForForumAtomFeed(LatestForumPostsForForumFeed):
    """
    Feed of latest forum's thread's posts for a given forum (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestForumPostsForForumFeed.description


class LatestForumPostsForThreadFeed(ForumPostsBaseFeed):
    """
    Feed of latest forum's thread's posts for a given forum's thread.
    """

    def get_object(self, request, *args, **kwargs):
        """
        Get the desired forum's thread.
        """

        # Get desired forum's thread PK
        pk = kwargs.pop('pk')
        slug = kwargs.pop('slug')
        assert pk is not None
        assert slug is not None

        # Get the forum's thread
        return ForumThread.objects.get(pk=pk, slug=slug, parent_forum__private=False)

    def title(self, obj):
        """
        Return the title of the forum's thread.
        """
        return _('Latest posts in forum thread "%s"') % obj.title

    def link(self, obj):
        """
        Return the permalink to the forum's thread.
        """
        return obj.get_absolute_url()

    def description(self, obj):
        """
        Return the description of the forum's thread.
        """
        return _('Latest posts in forum thread "%s"') % obj.title

    def items(self, obj):
        """
        Return a list of the N most recent (public) forum's thread's post in the given forum's thread.
        """
        return obj.posts.select_related('parent_thread__last_post',
                                        'parent_thread__first_post', 'author') \
                   .order_by('-pub_date')[:NB_FORUM_THREAD_POSTS_IN_FEEDS]


class LatestForumPostsForThreadAtomFeed(LatestForumPostsForThreadFeed):
    """
    Feed of latest forum's thread's posts for a given forum's thread (ATOM version).
    """
    feed_type = Atom1Feed
    subtitle = LatestForumPostsForThreadFeed.description
