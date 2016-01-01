"""
Data models managers for the forum app.
"""

import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .settings import (DELETED_THREAD_PHYSICAL_DELETION_TIMEOUT_DAYS,
                       DELETED_THREAD_POST_PHYSICAL_DELETION_TIMEOUT_DAYS)


class ForumManager(models.Manager):
    """
    Manager class for the ``Forum`` data model.
    """

    use_for_related_fields = True

    def root_forums(self):
        """
        Returns a queryset of all root forums, ordered for display.
        """
        return self.filter(parent=None)

    def public_forums(self):
        """
        Return a queryset of all public forums.
        """
        return self.filter(private=False)


class ForumThreadManager(models.Manager):
    """
    Manager class for the ``ForumThread`` data model.
    """

    use_for_related_fields = True

    def published(self):
        """
        Returns a queryset with all published (non deleted) threads.
        """
        return self.filter(deleted_at__isnull=True)

    def public_threads(self):
        """
        Return a queryset of all published public threads.
        """
        return self.published().filter(parent_forum__isnull=False, parent_forum__private=False)

    def display_ordered(self, forum):
        """
        Return all threads of the given forum ordered for display.
        """
        return self.published().filter(Q(global_sticky=True) | Q(parent_forum=forum)) \
            .order_by('-sticky', '-last_post__last_modification_date')

    @staticmethod
    def create_thread(parent_forum, title, author, pub_date, content, author_ip_address,
                      sticky=False, closed=False, resolved=False, locked=False):
        """
        Create a new forum's thread and his related first post.
        :param parent_forum: The parent forum instance.
        :param title: The new thread title.
        :param author: The new thread author.
        :param pub_date: The new thread publication date.
        :param content: The new thread content.
        :param author_ip_address: The new thread author IP address.
        :param sticky: The new thread sticky flag.
        :param closed: The new thread closed flag.
        :param resolved: The new thread resolved flag.
        :param locked: The new thread locked flag.
        """

        # Import here to avoid circular dependency
        from .models import ForumThread, ForumThreadPost

        # Create the first post (step 1/3)
        new_first_post = ForumThreadPost.objects.create(author=author,
                                                        pub_date=pub_date,
                                                        content=content,
                                                        author_ip_address=author_ip_address)

        # Create the new thread (step 2/3)
        new_thread = ForumThread.objects.create(parent_forum=parent_forum,
                                                title=title,
                                                sticky=sticky,
                                                closed=closed,
                                                resolved=resolved,
                                                locked=locked,
                                                first_post=new_first_post,
                                                last_post=new_first_post)

        # Update the first post to set the parent thread (step 3/3)
        new_first_post.parent_thread = new_thread
        new_first_post.save()

        # Return the newly created thread
        return new_thread

    def delete_deleted_threads(self, queryset=None):
        """
        Delete all deleted threads.
        :param queryset: The queryset to be processed, all() per default.
        :return: None
        """

        # Process all threads by default
        if queryset is None:
            queryset = self.all()

        # Deletion threshold date
        deletion_date = timezone.now() - datetime.timedelta(days=DELETED_THREAD_PHYSICAL_DELETION_TIMEOUT_DAYS)

        # Retrieve all threads to be physically deleted
        threads_to_be_deleted = queryset.filter(deleted_at__isnull=False,
                                                deleted_at__lte=deletion_date)

        # Deleted all flagged threads
        threads_to_be_deleted.delete()


class ForumThreadPostManager(models.Manager):
    """
    Manager class for the ``ForumThreadPost`` data model.
    """

    use_for_related_fields = True

    def published(self):
        """
        Returns a queryset with all published (non deleted) post.
        """
        return self.filter(deleted_at__isnull=True)

    def public_published(self):
        """
        Return a queryset with all publicly published (non deleted, not in private thread) post.
        """
        return self.published().filter(parent_thread__parent_forum__private=False)

    def delete_deleted_posts(self, queryset=None):
        """
        Delete all deleted thread posts.
        :param queryset: The queryset to be processed, all() per default.
        :return: None
        """

        # Process all posts by default
        if queryset is None:
            queryset = self.all()

        # Deletion threshold date
        deletion_date = timezone.now() - datetime.timedelta(days=DELETED_THREAD_POST_PHYSICAL_DELETION_TIMEOUT_DAYS)

        # Retrieve all posts to be physically deleted
        posts_to_be_deleted = queryset.filter(deleted_at__isnull=False,
                                              deleted_at__lte=deletion_date)

        # Deleted all flagged posts
        posts_to_be_deleted.delete()


class ForumSubscriptionManager(models.Manager):
    """
    Manager class for the ``ForumSubscription`` data model.
    """

    def get_subscribers_for_forum(self, forum):
        """
        Returns a queryset of all subscribers for the given forum.
        :param forum: The target forum.
        :return: A queryset of all subscribers for the given forum.
        """
        return self.filter(forum=forum, active=True)

    def has_subscribed_to_forum(self, user, forum):
        """
        Check if the given user has subscribed to the given forum or not.
        :param user: The user to check.
        :param forum: The forum to check.
        :return: ``True`` if the user has subscribed to the given forum, ``False`` otherwise.
        """
        return self.filter(user=user, forum=forum, active=True).exists()

    def subscribe_to_forum(self, user, forum):
        """
        Subscribe to the given forum.
        :param user: The subscriber.
        :param forum: The forum to subscribe for.
        :return: None
        """
        subscription, created = self.get_or_create(user=user, forum=forum)
        if not created:
            subscription.active = True
            subscription.save()

    def unsubscribe_from_forum(self, user, forum):
        """
        Unsubscribe from the given forum.
        :param user: The un-subscriber.
        :param forum: The forum to subscribe for.
        :return: None
        """
        self.filter(user=user, forum=forum).update(active=False)


class ForumThreadSubscriptionManager(models.Manager):
    """
    Manager class for the ``ForumThreadSubscription`` data model.
    """

    def get_subscribers_for_thread(self, thread):
        """
        Returns a queryset of all subscribers for the given forum's thread.
        :param thread: The target forum's thread.
        :return: A queryset of all subscribers for the given forum's thread.
        """
        return self.filter(thread=thread, active=True)

    def has_subscribed_to_thread(self, user, thread):
        """
        Check if the given ser has subscribed to the given forum thread or not.
        :param user: The user to check.
        :param thread: The forum thread to check.
        :return: ``True`` if the user has subscribed to the given forum thread, ``False`` otherwise.
        """
        return self.filter(user=user, thread=thread, active=True).exists()

    def subscribe_to_thread(self, user, thread):
        """
        Subscribe to the given forum thread.
        :param user: The subscriber.
        :param thread: The forum thread to subscribe for.
        :return: None
        """
        subscription, created = self.get_or_create(user=user, thread=thread)
        if not created:
            subscription.active = True
            subscription.save()

    def unsubscribe_from_thread(self, user, thread):
        """
        Unsubscribe from the given forum thread.
        :param user: The un-subscriber.
        :param thread: The forum thread to subscribe for.
        :return: None
        """
        self.filter(user=user, thread=thread).update(active=False)


class ReadForumTrackerManager(models.Manager):
    """
    Manager class for the ``ReadForumTracker`` data model.
    """

    def mark_forum_as_read(self, user, forum):
        """
        Mark the given forum as read for the specified user.
        :param user: The target user.
        :param forum: The forum to be marked as read.
        :return: None
        """
        marker, created = self.get_or_create(user=user, forum=forum)
        if not created:
            marker.active = True
            marker.last_read_date = timezone.now()
            marker.save()

    def mark_forum_as_unread(self, user, forum):
        """
        Mark the given thread as unread for the given user.
        :param user: The target user.
        :param forum: The forum to be marked as unread.
        :return: None
        """
        self.filter(user=user, thread=forum).update(active=False)

    def get_marker_for_forum(self, user, forum_id):
        """
        Get all "read" marker for the given forum's ID.
        :param user: The target user.
        :param forum_id: The forum's id for retrieving.
        :return: The last read date or None.
        """
        try:
            return self.get(user=user, active=True, forum=forum_id).last_read_date
        except ObjectDoesNotExist:
            return None

    def get_marker_for_forums(self, user, forum_ids):
        """
        Get all "read" marker for the given forum's IDs.
        :param user: The target user.
        :param forum_ids: A list of forum's id for retrieving.
        :return: A dict {thread_id: last_read_date}
        """
        return dict(self.filter(user=user, active=True, forum__in=forum_ids).values_list('forum__id',
                                                                                         'last_read_date'))


class ReadForumThreadTrackerManager(models.Manager):
    """
    Manager class for the ``ReadForumThreadTracker`` data model.
    """

    def mark_thread_as_read(self, user, thread):
        """
        Mark the given thread as read for the specified user.
        :param user: The target user.
        :param thread: The thread to be marked as read.
        :return: None
        """
        marker, created = self.get_or_create(user=user, thread=thread)
        if not created:
            marker.active = True
            marker.last_read_date = timezone.now()
            marker.save()

    def mark_thread_as_unread(self, user, thread):
        """
        Mark the given thread as unread for the given user.
        :param user: The target user.
        :param thread: The thread to be marked as unread.
        :return: None
        """
        self.filter(user=user, thread=thread).update(active=False)

    def get_marker_for_thread(self, user, thread_id):
        """
        Get all "read" marker for the given forum's thread ID.
        :param user: The target user.
        :param thread_id: The forum's thread id for retrieving.
        :return: The last read date or None.
        """
        try:
            return self.get(user=user, active=True, thread=thread_id).last_read_date
        except ObjectDoesNotExist:
            return None

    def get_marker_for_threads(self, user, thread_ids):
        """
        Get all "read" marker for the given thread's IDs.
        :param user: The target user.
        :param thread_ids: A list of thread's id for retrieving.
        :return: A dict {thread_id: last_read_date}
        """
        return dict(self.filter(user=user, active=True, thread__in=thread_ids).values_list('thread__id',
                                                                                           'last_read_date'))
