"""
Data models for the private messages app.
"""

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in

from apps.tools.fields import AutoOneToOneField
from apps.txtrender.fields import RenderTextField
from apps.txtrender.utils import render_html, strip_html
from apps.txtrender.signals import render_engine_changed

from .manager import (PrivateMessageManager,
                      BlockedUserManager)
from .settings import NB_SECONDS_BETWEEN_PRIVATE_MSG


class PrivateMessage(models.Model):
    """
    Private message data model.
    A private message is made of:
    - a subject, can be blank, in this case the string "(no subject)" translated is used.
    - a body text (source and HTML version),
    - a sender and a recipient,
    - a parent message, for next/previous navigation, ``replies`` attribute contain all child messages.
    - some "sent at", "read at", "replied at" flag date
    - also some "sender deleted at" and "recipient deleted at" flag date to handle logical deletion instead of
    physical deletion (keep trace of messages some time before cleanup CRON).
    """

    subject = models.CharField(_('Subject'),
                               max_length=255,
                               default='',
                               blank=True)

    body = RenderTextField(_('Message'))

    body_html = models.TextField(_('Message (raw HTML)'))

    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               db_index=True,  # Database optimization
                               related_name='privatemsg_sent',
                               verbose_name=_('Sender'))

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  db_index=True,  # Database optimization
                                  related_name='privatemsg_received',
                                  verbose_name=_('Recipient'))

    parent_msg = models.ForeignKey('PrivateMessage',
                                   db_index=True,  # Database optimization
                                   related_name='replies',
                                   verbose_name=_('Parent message'),
                                   default=None,
                                   null=True,
                                   blank=True,
                                   on_delete=models.SET_NULL)

    sent_at = models.DateTimeField(_('Sent at'),
                                   db_index=True,  # Database optimization
                                   auto_now_add=True)

    read_at = models.DateTimeField(_('Read at'),
                                   db_index=True,  # Database optimization
                                   default=None,
                                   null=True,
                                   blank=True)

    sender_deleted_at = models.DateTimeField(_('Sender deleted at'),
                                             db_index=True,  # Database optimization
                                             default=None,
                                             null=True,
                                             blank=True)

    recipient_deleted_at = models.DateTimeField(_('Recipient deleted at'),
                                                db_index=True,  # Database optimization
                                                default=None,
                                                null=True,
                                                blank=True)

    sender_permanently_deleted = models.BooleanField(_('Sender permanently deleted'),
                                                     default=False)

    recipient_permanently_deleted = models.BooleanField(_('Recipient permanently deleted'),
                                                        default=False)

    objects = PrivateMessageManager()

    class Meta:
        verbose_name = _('Private message')
        verbose_name_plural = _('Private messages')
        get_latest_by = 'sent_at'
        ordering = ('-sent_at', 'id')

    def __str__(self):
        return self.get_subject_display()

    def save(self, *args, **kwargs):
        """
        All the saving logic happen here.
        :param args: Positional super() parameters.
        :param kwargs: Named super() parameters.
        """

        # Avoid erroneous state
        now = timezone.now()
        if self.recipient_permanently_deleted and self.recipient_deleted_at is None:
            self.recipient_deleted_at = now
        if self.sender_permanently_deleted and self.sender_deleted_at is None:
            self.sender_deleted_at = now

        # Render the message's body text
        self.render_body()

        # Save the message
        super(PrivateMessage, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Return the permalink to this message.
        """
        return reverse('privatemsg:msg_detail', kwargs={'pk': self.pk})

    def get_reply_url(self):
        """
        Return the "reply" permalink for this message.
        """
        return reverse('privatemsg:msg_reply', kwargs={'parent_pk': self.pk})

    def get_delete_url(self):
        """
        Return the "delete" permalink for this message.
        """
        return reverse('privatemsg:msg_delete', kwargs={'pk': self.pk})

    def get_delete_permanent_url(self):
        """
        Return the "delete permanently" permalink for this message.
        """
        return reverse('privatemsg:msg_delete_permanent', kwargs={'pk': self.pk})

    def get_undelete_url(self):
        """
        Return the "un-delete" permalink for this message.
        """
        return reverse('privatemsg:msg_undelete', kwargs={'pk': self.pk})

    def get_subject_display(self):
        """
        Return the subject of the message for displaying.
        """
        return str(self.subject or _('(no subject)'))
    get_subject_display.short_description = _('Subject')
    get_subject_display.admin_order_field = 'subject'

    def unread(self):
        """
        Returns ``True`` if the recipient has read the message.
        """
        return self.read_at is None
    unread.short_description = _('Unread')
    unread.boolean = True

    def deleted_at_recipient_side(self):
        """
        Returns ``True`` if the recipient has deleted the message.
        """
        return self.recipient_deleted_at is not None or self.recipient_permanently_deleted
    deleted_at_recipient_side.short_description = _('Deleted at recipient side')
    deleted_at_recipient_side.boolean = True

    def deleted_at_sender_side(self):
        """
        Returns ``True`` if the sender has deleted the message.
        """
        return self.sender_deleted_at is not None or self.sender_permanently_deleted
    deleted_at_sender_side.short_description = _('Deleted at sender side')
    deleted_at_sender_side.boolean = True

    def is_recipient(self, user):
        """
        Return ``True`` if the given user is the recipient of this message.
        """
        return user == self.recipient

    def is_sender(self, user):
        """
        Return ``True`` if the given user is the sender of this message.
        """
        return user == self.sender

    def deleted_from_user_side(self, user):
        """
        Returns ``True`` if the user has deleted this message.
        """
        if user == self.recipient:
            return self.deleted_at_recipient_side()
        elif user == self.sender:
            return self.deleted_at_sender_side()
        return False

    def permanently_deleted_from_user_side(self, user):
        """
        Returns ``True`` if the user has permanently deleted this message.
        """
        if user == self.recipient:
            return self.recipient_permanently_deleted
        elif user == self.sender:
            return self.sender_permanently_deleted
        return False

    def delete_from_user_side(self, user, permanent=False):
        """
        Delete the message from the given user side.
        Given user should be the recipient or sender for this function to work.
        :param user: The user to delete this message from.
        """
        if user == self.recipient:
            if self.recipient_deleted_at is None:
                self.recipient_deleted_at = timezone.now()
            if not self.recipient_permanently_deleted:
                self.recipient_permanently_deleted = permanent
        elif user == self.sender:
            if self.sender_deleted_at is None:
                self.sender_deleted_at = timezone.now()
            if not self.sender_permanently_deleted:
                self.sender_permanently_deleted = permanent

    def undelete_from_user_side(self, user, permanent=False):
        """
        Un-delete the message from the given user side.
        Given user should be the recipient or sender for this function to work.
        :param user: The user to undelete this message from.
        """
        if user == self.recipient:
            self.recipient_deleted_at = None
            self.recipient_permanently_deleted = False
        elif user == self.sender:
            self.sender_deleted_at = None
            self.sender_permanently_deleted = False

    def render_body(self, save=False):
        """
        Render the content. Save the model only if ``save`` is True.
        """

        # Render HTML
        self.body_html = render_html(self.body)

        # Save if required
        if save:
            # Avoid infinite loop by calling directly super.save
            super(PrivateMessage, self).save(update_fields=('body_html',))

    @cached_property
    def get_body_without_html(self):
        """
        Return the private message's text without any HTML tag nor entities.
        """
        return strip_html(self.body_html)


def _redo_private_messages_text_rendering(sender, **kwargs):
    """
    Redo text rendering of all private messages.
    :param sender: Not used.
    :param kwargs: Not used.
    """
    for message in PrivateMessage.objects.all():
        message.render_body(save=True)


render_engine_changed.connect(_redo_private_messages_text_rendering)


def notice_unread_messages_upon_login(sender, user, request, **kwargs):
    """
    Add an INFO flash message upon user login if the user has unread messages.
    :param sender: Not used.
    :param user: The logged-in user.
    :param request: The current request.
    :param kwargs: Not used.
    :return: None
    """
    unread_count = PrivateMessage.objects.inbox_count_for(user)
    if unread_count > 0:
        messages.add_message(request, messages.INFO, mark_safe(
            _('You have %(count)d unread private messages '
              '<a href="%(link)s" class="alert-link">Click here to see them</a>.') % {
                'count': unread_count,
                'link': reverse('privatemsg:inbox_unread')
            }))


user_logged_in.connect(notice_unread_messages_upon_login)


class PrivateMessageUserProfile(models.Model):
    """
    Private messages user's profile data model.
    """

    user = AutoOneToOneField(settings.AUTH_USER_MODEL,
                             related_name='privatemsg_profile',
                             editable=False,
                             primary_key=True,
                             verbose_name=_('Related user'))

    notify_on_new_privmsg = models.BooleanField(_('Notify me of new private message'),
                                                default=True)

    accept_privmsg = models.BooleanField(_('Accept incoming private message'),
                                         default=True)

    last_sent_private_msg_date = models.DateTimeField(_('Last sent private msg date'),
                                                      default=None,
                                                      blank=True,
                                                      null=True)

    class Meta:
        verbose_name = _('Private messages user profile')
        verbose_name_plural = _('Private messages user profiles')

    def __str__(self):
        return 'Private messages user profile of "%s"' % self.user.username

    def is_flooding(self, now=None):
        """
        Returns ``True`` if the user has post something less than ``NB_SECONDS_BETWEEN_PRIVATE_MSG`` seconds from now.
        Returns ``False`` if the user has never post something.
        :param now: For testing purpose only.
        :return: bool ``True`` if the user is flooding (= trying to post two messages before the
        ``NB_SECONDS_BETWEEN_PRIVATE_MSG`` seconds delay is reached).
        """
        if self.last_sent_private_msg_date is None:
            return False
        if now is None:
            now = timezone.now()
        delta = now - self.last_sent_private_msg_date
        return delta.total_seconds() < NB_SECONDS_BETWEEN_PRIVATE_MSG

    def rearm_flooding_delay_and_save(self):
        """
        Re-arm the anti flood delay and save the model.
        """
        self.last_sent_private_msg_date = timezone.now()
        self.save()


class BlockedUser(models.Model):
    """
    Blocked user data model.
    Allow users to disallow other users to sent message to us.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='blocked_users',
                             editable=False,
                             verbose_name=_('Related user'))

    blocked_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='blockedby_users',
                                     editable=False,
                                     verbose_name=_('Blocked user'))

    last_block_date = models.DateTimeField(_('Last block date'))

    active = models.BooleanField(_('Active'),
                                 default=True)

    objects = BlockedUserManager()

    class Meta:
        unique_together = (('user', 'blocked_user'),)
        verbose_name = _('Blocked user')
        verbose_name_plural = _('Blocked users')
        get_latest_by = 'last_block_date'
        ordering = ('-active', '-last_block_date')

    def __str__(self):
        return 'User "%s" blocking "%s"' % (self.user.username, self.blocked_user.username)

    def save(self, *args, **kwargs):
        """
        Save the model.
        :param args: For super()
        :param kwargs: For super()
        :return: None
        """

        # Fix last block date on create
        if self.last_block_date is None:
            self.last_block_date = timezone.now()

        # Save the model
        super(BlockedUser, self).save(*args, **kwargs)
