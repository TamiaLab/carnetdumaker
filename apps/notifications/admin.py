"""
Admin models for the notifications app.
"""

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import (Notification,
                     NotificationsUserProfile)


class NotificationAdmin(admin.ModelAdmin):
    """
    Custom admin model for the ``Notification`` model.
    """

    list_select_related = ('recipient',)

    list_display = ('title',
                    'recipient_username_link',
                    'notification_date',
                    'unread')

    list_filter = ('notification_date',
                   'unread')

    search_fields = ('recipient__email',
                     'recipient__username',
                     'title',
                     'message',
                     'dismiss_code')

    raw_id_fields = ('recipient',)

    readonly_fields = ('notification_date',)

    def save_model(self, request, obj, form, change):
        """
        Save the notification object.
        :param request: The current request.
        :param obj: The new object to be saved.
        :param form: The parent form instance.
        :param change: ``True`` if an existing instance is edited, not created.
        :return: None
        """
        obj.save()
        if not change:
            self._send_notification_by_mail(obj, request)

    @staticmethod
    def _send_notification_by_mail(obj, request):
        """
        Helper use to send the notification mail. Overload this function to change default
        parameters passed to ``send_notification_by_mail``.
        :param obj: The newly created notification.
        :param request: The current request.
        :return: None
        """
        obj.send_notification_by_mail(request)

    def recipient_username_link(self, obj):
        """
        Return the username of the related notification's recipient as a link to the related user admin edit page.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=[obj.recipient.pk]), obj.recipient.username)
    recipient_username_link.short_description = _('Recipient')
    recipient_username_link.admin_order_field = 'recipient__username'
    recipient_username_link.allow_tags = True


class NotificationsUserProfileAdmin(admin.ModelAdmin):
    """
    ``NotificationsUserProfile`` admin form.
    """

    list_select_related = ('user',)

    list_display = ('user_username',
                    'send_mail_on_new_notification')

    list_filter = ('send_mail_on_new_notification',)

    search_fields = ('user__email',
                     'user__username')

    readonly_fields = ('user_username',)

    fields = ('user_username',
              'send_mail_on_new_notification')

    def user_username(self, obj):
        """
        Return the related user's username.
        :param obj: Current ticket object.
        :return: Relate user's username.
        """
        return obj.user.username
    user_username.short_description = _('Related user')
    user_username.admin_order_field = 'user__username'


admin.site.register(NotificationsUserProfile, NotificationsUserProfileAdmin)
admin.site.register(Notification, NotificationAdmin)
