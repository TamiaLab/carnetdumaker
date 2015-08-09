"""
Custom template tag for the forum app.
"""

from django import template


register = template.Library()


@register.filter
def has_access_to(user, forum_or_thread):
    """
    Return True if the user has access to this forum or thread.
    :param user: The current user.
    :param forum_or_thread: The forum or thread instance.
    :return: bool True if the given user has access to the given forum or thread.
    """
    return forum_or_thread.has_access(user)


@register.filter
def can_edit(user, thread_or_post):
    """
    Return True if the user can edit this post.
    :param user: The current user.
    :param thread_or_post: The thread or post instance.
    :return: bool True if the given user can edit this thread or post.
    """
    return thread_or_post.can_edit(user)


@register.filter
def can_delete(user, thread_or_post):
    """
    Return True if the user can edit this post.
    :param user: The current user.
    :param thread_or_post: The thread or post instance.
    :return: bool True if the given user can edit this thread or post.
    """
    return thread_or_post.can_delete(user)


@register.filter
def can_delete(user, post):
    """
    Return True if the user can see the author's IP address of this post.
    :param user: The current user.
    :param post: The post instance.
    :return: bool True if the given user can edit this thread or post.
    """
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
            and parent_forum_last_read_date > last_modification_date:
        return True

    # The user has not read this thread yet if no marker exist
    if last_read_date is None:
        return False

    # If the marker exist, check the last update date
    return last_read_date >= last_modification_date
