"""
Admin models for the private messages app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .models import (PrivateMessage,
                     PrivateMessageUserProfile,
                     BlockedUser)
from .notifications import notify_of_new_private_message


class PrivateMessageAdmin(admin.ModelAdmin):
    """
    Custom admin model for the ``PrivateMessage`` model.
    """

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Overload to pre-fill initial author with the current user PK.
        :param db_field: The current db field.
        :param request: The current request.
        :param kwargs: Extra named parameters.
        :return: super() result.
        """
        if db_field.name == 'sender':
            kwargs['initial'] = request.user.id
        return super(PrivateMessageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Save the model.
        :param request: The current request.
        :param obj: The current model object to be saved.
        :param form: The parent form instance.
        :param change: True if the form has changed.
        :return: None
        """

        # Save the model
        obj.save()

        # Notify subscribers of new private msg
        if not change:
            notify_of_new_private_message(obj, request)

    list_select_related = ('sender',
                           'recipient')

    list_display = ('get_subject_display',
                    'sender_username_link',
                    'recipient_username_link',
                    'sent_at',
                    'read_at',
                    'sender_deleted_at',
                    'recipient_deleted_at',
                    'sender_permanently_deleted',
                    'recipient_permanently_deleted')

    list_filter = ('sent_at',
                   'read_at',
                   'sender_deleted_at',
                   'recipient_deleted_at',
                   'sender_permanently_deleted',
                   'recipient_permanently_deleted')

    search_fields = ('recipient__email',
                     'recipient__username',
                     'sender__email',
                     'sender__username',
                     'subject',
                     'body')

    readonly_fields = ('get_subject_display',
                       'sender_username_link',
                       'recipient_username_link',
                       'sent_at')

    raw_id_fields = ('sender',
                     'recipient',
                     'parent_msg')

    fieldsets = (
        (_('Message'), {
            'fields': ('subject',
                       'body',
                       'parent_msg')
        }),
        (_('Recipient and sender'), {
            'fields': ('recipient',
                       'sender')
        }),
        (_('Date and time'), {
            'fields': ('sent_at',
                       'read_at',
                       'sender_deleted_at',
                       'recipient_deleted_at',
                       'sender_permanently_deleted',
                       'recipient_permanently_deleted')
        }),
    )

    def recipient_username_link(self, obj):
        """
        Return a link to the recipient user.
        :param obj: Current ticket object.
        :return: HTML <a> link.
        """
        user = obj.recipient
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:auth_user_change', args=[user.pk]),
                           user.username)
    recipient_username_link.short_description = _('Recipient')
    recipient_username_link.admin_order_field = 'recipient__username'
    recipient_username_link.allow_tags = True

    def sender_username_link(self, obj):
        """
        Return a link to the sender user.
        :param obj: Current ticket object.
        :return: HTML <a> link.
        """
        user = obj.sender
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:auth_user_change', args=[user.pk]),
                           user.username)
    sender_username_link.short_description = _('Sender')
    sender_username_link.admin_order_field = 'sender__username'
    sender_username_link.allow_tags = True


class PrivateMessageUserProfileAdmin(admin.ModelAdmin):
    """
    ``PrivateMessageUserProfile`` admin form.
    """

    list_select_related = ('user',)

    list_display = ('user_username',
                    'notify_on_new_privmsg',
                    'accept_privmsg',
                    'last_sent_private_msg_date')

    list_filter = ('notify_on_new_privmsg',
                   'accept_privmsg',
                   'last_sent_private_msg_date')

    search_fields = ('user__email',
                     'user__username')

    readonly_fields = ('user_username',)

    fields = ('user_username',
              'notify_on_new_privmsg',
              'accept_privmsg',
              'last_sent_private_msg_date')

    def user_username(self, obj):
        """
        Return the related user's username.
        :param obj: Current ticket object.
        :return: Relate user's username.
        """
        return obj.user.username
    user_username.short_description = _('Related user')
    user_username.admin_order_field = 'user__username'


admin.site.register(BlockedUser)
admin.site.register(PrivateMessage, PrivateMessageAdmin)
admin.site.register(PrivateMessageUserProfile, PrivateMessageUserProfileAdmin)
