"""
Data models for the notifications app.
"""

from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.shortcuts import get_current_site
from django.utils.safestring import mark_safe
from django.utils.translation import override
from django.utils.translation import ugettext_lazy as _
from django.template import loader

from apps.tools.fields import AutoOneToOneField

from .managers import NotificationManager
from .signals import (dismiss_notification,
                      unread_notification)


class Notification(models.Model):
    """
    Notification data model.
    A notification is made of:
    - a recipient,
    - a title,
    - a message (beware of user language!), HTML and text versions (for mailing),
    - a notification date,
    - a dismiss code,
    - an "unread" flag.
    """

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  db_index=True,  # Database optimization
                                  editable=False,
                                  related_name='notifications',
                                  verbose_name=_('Recipient'))

    notification_date = models.DateTimeField(_('Notification date'),
                                             db_index=True,  # Database optimization
                                             auto_now_add=True)

    unread = models.BooleanField(_('Unread'),
                                 default=True)

    dismiss_code = models.CharField(_('Dismiss code'),
                                    max_length=255,
                                    db_index=True,  # Database optimization
                                    editable=False,
                                    default='')

    title = models.CharField(_('Title'),
                             max_length=255)

    message = models.TextField(_('Message (plain text)'))

    message_html = models.TextField(_('Message (raw HTML)'))

    objects = NotificationManager()

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        get_latest_by = 'notification_date'
        ordering = ('-notification_date', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Returns the permalink to this notification.
        """
        return reverse('notifications:notification_detail', kwargs={'pk': self.pk})

    def __init__(self, *args, **kwargs):
        """
        Backup ``self.unread`` for dismiss/unread detection.
        :param args: For super()
        :param kwargs: For super()
        """
        super(Notification, self).__init__(*args, **kwargs)
        self._old_unread = self.unread

    def save(self, *args, **kwargs):
        """
        Save the model, send signals ``dismiss_notification`` or ``unread_notification`` if necessary.
        :param args: For super()
        :param kwargs: For super()
        :return: super()
        """

        # Save the model
        res = super(Notification, self).save(*args, **kwargs)

        # Detect unread changes
        if self._old_unread and not self.unread:
            dismiss_notification.send(sender=Notification, notification=self)
        elif self.unread and not self._old_unread:
            unread_notification.send(sender=Notification, notification=self)

        # Return super()
        return res

    def send_notification_by_mail(self, request,
                                  mail_subject_template_name='notifications/email_notification_subject.txt',
                                  mail_body_template_name='notifications/email_notification_body.txt',
                                  mail_body_template_name_html='notifications/email_notification_body.html',
                                  extra_context=None,
                                  use_https=False,
                                  from_email=None,
                                  reply_to=None):
        """
        Send the notification to the user by mail.
        :param request: The current request (used to determine the site domain).
        :param mail_subject_template_name: The template name to be used for the mail's subject.
        :param mail_body_template_name: The template name to be used for the mail's body.
        :param mail_body_template_name_html: The template name to be used for the mail's body (HTML version).
        :param extra_context: Any extra context for the template.
        :param use_https: Set to ``True`` if HTTPS must be used for urls.
        :param from_email: Set to something not None to overwrite the default ``from`` address.
        :param reply_to: "Reply-to" email address.
        """

        # Prepare context for the text rendering
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'email': self.recipient.email,
            'domain': domain,
            'site_name': site_name,
            'recipient': self.recipient,
            'protocol': 'https' if use_https else 'http',
            'notification': self,
        }
        if extra_context:
            context.update(extra_context)

        # Render the notification and the notification's mail in the preferred recipient user language
        with override(self.recipient.user_profile.preferred_language):

            mail_subject = loader.render_to_string(mail_subject_template_name, context)
            # Email subject *must not* contain newlines
            mail_subject = ''.join(mail_subject.splitlines())
            mail_body = loader.render_to_string(mail_body_template_name, context)
            mail_body_html = loader.render_to_string(mail_body_template_name_html, context)

        # craft the email and send it
        email_message = EmailMultiAlternatives(mail_subject,
                                               mail_body, from_email,
                                               [self.recipient.email],
                                               reply_to=reply_to)
        email_message.attach_alternative(mail_body_html, 'text/html')
        email_message.send(fail_silently=True)


def notice_unread_notifications_upon_login(sender, user, request, **kwargs):
    """
    Add an INFO flash message upon user login if the user has unread notifications.
    :param sender: Not used.
    :param user: The logged-in user.
    :param request: The current request.
    :param kwargs: Not used.
    :return: None
    """
    unread_count = Notification.objects.unread_notifications_count(user)
    if unread_count > 0:
        messages.add_message(request, messages.INFO, mark_safe(
            _('You have %(count)d unread notifications '
              '<a href="%(link)s" class="alert-link">Click here to see them</a>.') % {
                'count': unread_count,
                'link': reverse('notifications:notification_unread_list')
            }), extra_tags='unread_notifications', fail_silently=True)


user_logged_in.connect(notice_unread_notifications_upon_login)


class NotificationsUserProfile(models.Model):
    """
    Notifications user's profile data model.
    """

    user = AutoOneToOneField(settings.AUTH_USER_MODEL,
                             related_name='notifications_profile',
                             primary_key=True,
                             editable=False,
                             verbose_name=_('Related user'))

    send_mail_on_new_notification = models.BooleanField(_('Send mail on new notification'),
                                                        default=True)

    class Meta:
        verbose_name = _('Notification user profile')
        verbose_name_plural = _('Notification user profiles')
