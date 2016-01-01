"""
Custom template tag for the forum app.
"""

from django import template

from ..models import (ForumThread,
                      ForumThreadPost)
from ..settings import (NB_FORUM_THREAD_PER_PAGE_WIDGET,
                        NB_FORUM_POST_PER_PAGE_WIDGET)


register = template.Library()


@register.filter
def has_access_to(user, forum_or_thread):
    """
    Return True if the user has access to this forum or thread.
    :param user: The current user.
    :param forum_or_thread: The forum or thread instance.
    :return: bool True if the given user has access to the given forum or thread.
    """
    if user is None or forum_or_thread is None:
        return False
    return forum_or_thread.has_access(user)


@register.filter
def can_edit(user, thread_or_post):
    """
    Return True if the user can edit this post.
    :param user: The current user.
    :param thread_or_post: The thread or post instance.
    :return: bool True if the given user can edit this thread or post.
    """
    if user is None or thread_or_post is None:
        return False
    return thread_or_post.can_edit(user)


@register.filter
def can_delete(user, thread_or_post):
    """
    Return True if the user can edit this post.
    :param user: The current user.
    :param thread_or_post: The thread or post instance.
    :return: bool True if the given user can edit this thread or post.
    """
    if user is None or thread_or_post is None:
        return False
    return thread_or_post.can_delete(user)


@register.filter
def can_delete(user, post):
    """
    Return True if the user can see the author's IP address of this post.
    :param user: The current user.
    :param post: The post instance.
    :return: bool True if the given user can edit this thread or post.
    """
    if user is None or post is None:
        return False
    return post.can_see_ip_adress(user)


@register.filter
def has_been_read(thread, args_dict):
    """
    Return True if the user has read the given thread.
    :param thread: The target thread.
    :param args_dict: A dict ``{ parent_forum_last_read_date: datetime, thread_markers: {thread_id: last_read_date} }``
    :return: bool True if the user has read this thread.
    """

    # Get the parent forum thread "read" marker if any
    parent_forum_last_read_date = args_dict['parent_forum_last_read_date']

    # Get the last post modification date
    last_modification_date = thread.last_post.last_modification_date

    # Get the "read" marker for this thread, if any
    last_read_date = args_dict['thread_markers'].get(thread.id, None)

    # Check for modification made after the last "mark forum as read" action
    if parent_forum_last_read_date is not None \
            and parent_forum_last_read_date >= last_modification_date:
        return True

    # The user has not read this thread yet if no marker exist
    if last_read_date is None:
        return False

    # If the marker exist, check the last update date
    return last_read_date >= last_modification_date


@register.assignment_tag
def recent_forum_threads_list(nb_objects=NB_FORUM_THREAD_PER_PAGE_WIDGET):
    """
    Returns a list of all N recently published forum threads.
    :param nb_objects: The maximum number of objects to be returned.
    :return: A list of all N recently published forum threads.
    """
    return ForumThread.objects.public_threads().select_related('first_post__author',
                                                               'first_post__last_modification_by',
                                                               'last_post__author',
                                                               'last_post__last_modification_by')[:nb_objects]


@register.assignment_tag
def recent_forum_posts_list(nb_objects=NB_FORUM_POST_PER_PAGE_WIDGET):
    """
    Returns a list of all N recently published forum posts.
    :param nb_objects: The maximum number of objects to be returned.
    :return: A list of all N recently published forum posts.
    """
    return ForumThreadPost.objects.public_published() \
                   .select_related('parent_thread__first_post__author',
                                   'parent_thread__first_post__last_modification_by',
                                   'author', 'last_modification_by')[:nb_objects]
