"""
Data models managers for the notifications app.
"""

import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import override
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site

from .settings import READ_NOTIFICATION_DELETION_TIMEOUT_DAYS
from .signals import (new_notification,
                      dismiss_notification)


class NotificationManager(models.Manager):
    """
    Manager class for the ``Notification`` data model.
    """

    use_for_related_fields = True

    def send_notification_to_user(self, request, user,
                                  title_template_name,
                                  message_template_name,
                                  message_template_name_html,
                                  extra_context=None,
                                  dismiss_code='',
                                  use_https=False,
                                  kwargs_send_mail=None):
        """
        Send a new notification to the given user.
        :param request: The current request.
        :param user: The notification's recipient.
        :param title_template_name: The notification's title template name to be used.
        :param message_template_name: The notification's message template name to be used (text version). Only used
        for the notification email body.
        :param message_template_name_html: The notification's message template name to be used (HTML version).
        :param dismiss_code: Dismiss code for this notification.
        :param extra_context: Extra context arguments to be used when rendering the notification.
        :param use_https: Set to ``True`` to use HTTPS for urls.
        :param kwargs_send_mail: Custom kwargs for the send_notification_by_mail() function.
        :return: The newly created notification, or ``None`` if the user is not active.
        """

        # Cannot send notification to inactive users
        if not user.is_active:
            return None

        # Prepare context for the text rendering
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'domain': domain,
            'site_name': site_name,
            'protocol': 'https' if use_https else 'http',
            }
        if extra_context:
            context.update(extra_context)

        # Render the notification text in the preferred recipient user language
        with override(user.user_profile.preferred_language):
            title = loader.render_to_string(title_template_name, context)
            message = loader.render_to_string(message_template_name, context)
            message_html = loader.render_to_string(message_template_name_html, context)

        # Create the notification
        new_obj = self.create(recipient=user, title=title,
                              message=message, message_html=message_html,
                              dismiss_code=dismiss_code)
        new_notification.send(sender=NotificationManager, notification=new_obj)

        # Send the notification by mail (with or without custom args)
        if user.notifications_profile.send_mail_on_new_notification:
            if kwargs_send_mail is not None:
                new_obj.send_notification_by_mail(request, **kwargs_send_mail)
            else:
                new_obj.send_notification_by_mail(request)

        # Return the newly created object
        return new_obj

    def has_unread_notification(self, user):
        """
        Check if the given user has unread notifications.
        :param user: The user to be checked.
        :return: ``True`` if the user has unread notifications, ``False`` otherwise.
        """
        return self.filter(recipient=user, unread=True).exists()

    def unread_notifications_count(self, user):
        """
        Return the number of unread notifications for the given user.
        :param user: The user to be checked.
        :return: The number of unread notifications.
        """
        return self.filter(recipient=user, unread=True).count()

    def mark_all_notifications_has_read(self, user):
        """
        Mark all notification of the given user as read.
        :param user: The user to be processed.
        :return: The number of notifications updated.
        """
        return self.filter(recipient=user).update(unread=False)

    def delete_old_notifications(self, queryset=None):
        """
        Delete old notifications.
        :param queryset: The queryset to be processed, if None all notifications are processed.
        :return: None
        """
        if not queryset:
            queryset = self.all()
        deletion_date_threshold = timezone.now() - datetime.timedelta(days=READ_NOTIFICATION_DELETION_TIMEOUT_DAYS)
        queryset.filter(notification_date__lte=deletion_date_threshold).delete()

    def dismiss_notifications(self, user, dismiss_code):
        """
        Dismiss any notifications with the given ``user `` and ``dismiss_code``.
        :param user: The target user.
        :param dismiss_code: The target dismiss code.
        :return: None
        """
        queryset = self.filter(recipient=user, dismiss_code=dismiss_code)
        for notification in queryset:
            dismiss_notification.send(sender=NotificationManager, notification=notification)
        queryset.update(unread=False)
