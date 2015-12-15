"""
Data model objects manager for the private messages app.
"""

import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone

from .settings import (DELETED_MSG_DELETION_TIMEOUT_DAYS,
                       DELETED_MSG_PHYSICAL_DELETION_TIMEOUT_DAYS)


class PrivateMessageManager(models.Manager):
    """
    Objects manager for the ``PrivateMessage`` data model.
    """

    def inbox_count_for(self, user):
        """
        Returns the number of unread messages for the given user.
        :param user: The target user.
        :return: The number of unread messages.
        """
        return self.filter(recipient=user,
                           read_at__isnull=True,
                           recipient_deleted_at__isnull=True,
                           recipient_permanently_deleted=False).count()

    def inbox_for(self, user):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        :param user: The target user.
        """
        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=True,
            recipient_permanently_deleted=False
        )

    def mark_all_messages_has_read(self, user):
        """
        Mark all private messages of the given user as read.
        :param user: The target user.
        :return: The number of messages marked as read.
        """
        now = timezone.now()
        return self.filter(recipient=user,
                           read_at__isnull=True,
                           recipient_deleted_at__isnull=True,
                           recipient_permanently_deleted=False).update(read_at=now)

    def outbox_for(self, user):
        """
        Returns all messages that were sent by the given user and are not
        marked as deleted.
        :param user: The target user.
        """
        return self.filter(
            sender=user,
            sender_deleted_at__isnull=True,
            sender_permanently_deleted=False
        )

    def trash_for(self, user):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.
        :param user: The target user.
        """
        logical_deletion_date = timezone.now() - datetime.timedelta(days=DELETED_MSG_DELETION_TIMEOUT_DAYS)
        return self.filter(Q(
            recipient=user,
            recipient_deleted_at__isnull=False,
            recipient_deleted_at__gt=logical_deletion_date,
            recipient_permanently_deleted=False
        ) | Q(
            sender=user,
            sender_deleted_at__isnull=False,
            sender_deleted_at__gt=logical_deletion_date,
            sender_permanently_deleted=False
        ))

    def empty_trash_of(self, user):
        """
        Empty the trash box of the given user.
        :param user: The target user.
        :return: None
        """
        self.filter(
            recipient=user,
            recipient_deleted_at__isnull=False,
            recipient_permanently_deleted=False
        ).update(recipient_permanently_deleted=True)
        self.filter(
            sender=user,
            sender_deleted_at__isnull=False,
            sender_permanently_deleted=False
        ).update(sender_permanently_deleted=True)

    def delete_deleted_msg(self, queryset=None):
        """
        Delete all deleted messages.
        :param queryset: The queryset to be processed, all() per default.
        :return: None
        """

        # Process all messages by default
        if queryset is None:
            queryset = self.all()

        # Deletion threshold date
        logical_deletion_date = timezone.now() - datetime.timedelta(days=DELETED_MSG_DELETION_TIMEOUT_DAYS)
        physical_deletion_date = timezone.now() - datetime.timedelta(days=DELETED_MSG_PHYSICAL_DELETION_TIMEOUT_DAYS)

        # Retrieve all message to be physically deleted
        msg_to_be_deleted = queryset.filter(recipient_deleted_at__isnull=False,
                                            recipient_deleted_at__lte=physical_deletion_date,
                                            sender_deleted_at__isnull=False,
                                            sender_deleted_at__lte=physical_deletion_date)

        # Deleted all flagged messages
        msg_to_be_deleted.delete()

        # Hide remaining old messages from user trash
        queryset.filter(recipient_deleted_at__isnull=False,
                        recipient_deleted_at__lte=logical_deletion_date).update(recipient_permanently_deleted=True)
        queryset.filter(sender_deleted_at__isnull=False,
                        sender_deleted_at__lte=logical_deletion_date).update(sender_permanently_deleted=True)


class BlockedUserManager(models.Manager):
    """
    Manager class for the ``BlockedUser`` data model.
    """

    use_for_related_fields = True

    def blocked_users_for(self, user):
        """
        Returns a queryset of all currently blocked user of the given user.
        :param user: The target user.
        """
        return self.filter(user=user, active=True)

    def has_blocked_user(self, user, other_user):
        """
        Check if the given user has block to the given user or not.
        :param user: The user to check.
        :param other_user: The other user to check for blocking by the first one.
        :return: ``True`` if the user has blocked to the given user, ``False`` otherwise.
        """
        return self.filter(user=user, blocked_user=other_user, active=True).exists()

    def block_user(self, user, other_user):
        """
        Block to the given user.
        :param user: The user blocking the other user.
        :param other_user: The user being blocked by ``user``.
        :return: None
        """
        block_obj, created = self.get_or_create(user=user, blocked_user=other_user)
        if not created:
            block_obj.last_block_date = timezone.now()
            block_obj.active = True
            block_obj.save()

    def unblock_user(self, user, other_user):
        """
        Unblock to the given user.
        :param user: The user currently blocking the other user.
        :param other_user: The user being unblocked by ``user``.
        :return: None
        """
        self.filter(user=user, blocked_user=other_user).update(active=False)
