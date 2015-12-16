"""
Admin models for the registration app.
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import (UserRegistrationProfile,
                     BannedUsername,
                     BannedEmail)


class RegistrationAdmin(admin.ModelAdmin):
    """
    Admin page for the registration mechanism.
    This admin page allow management and manual activation of various user
    registration profiles.
    """

    actions = ('activate_users',
               'resend_activation_emails',
               'force_resend_activation_emails',
               'delete_expired_users')

    list_display = ('user',
                    'activation_key_used',
                    'activation_key_expired',
                    'last_key_mailing_date',
                    'creation_date',
                    'activation_mail_was_sent_recently')

    raw_id_fields = ('user', )

    search_fields = ('user__email',
                     'user__username',
                     'activation_key')

    list_filter = ('activation_key_used',
                   'last_key_mailing_date',
                   'creation_date')

    readonly_fields = ('user',
                       'activation_key',
                       'activation_key_used',
                       'last_key_mailing_date')

    def activate_users(self, request, queryset):
        """
        Activates the selected users, if they are not already activated.
        :param request: Current request.
        :param queryset: Selected objects queryset.
        """
        activated_users_count = 0
        for profile in queryset:
            profile.activate_user()
            activated_users_count += 1
        self.message_user(request, _('%d users were successfully activated.') % activated_users_count)
    activate_users.short_description = _("Activate users")

    def resend_activation_emails(self, request, queryset):
        """
        Re-sends activation emails for the selected users.
        Note that this will *only* send activation emails for users
        who are eligible to activate; emails will not be sent to users
        whose activation keys have expired or who have already
        activated.
        :param request: Current request.
        :param queryset: Selected objects queryset.
        """
        email_sent_count = 0
        for profile in queryset:
            if not profile.activation_key_expired() and not profile.user.is_active:
                self._send_email(request, profile)
                email_sent_count += 1
        self.message_user(request, _('%d emails successfully sent.') % email_sent_count)
    resend_activation_emails.short_description = _("Re-send activation emails")

    def force_resend_activation_emails(self, request, queryset):
        """
        Re-sends activation emails for the selected users.
        Note that this will send activation emails for any users
        who have not already used their activation key, effectively
        resetting their activation link expiration date.
        :param request: Current request.
        :param queryset: Selected objects queryset.
        """
        email_sent_count = 0
        for profile in queryset:
            if not profile.activation_key_used:
                self._send_email(request, profile)
                email_sent_count += 1
        self.message_user(request, _('%d emails successfully sent.') % email_sent_count)
    force_resend_activation_emails.short_description = _("Reset expiration date and re-send activation emails")

    @staticmethod
    def _send_email(request, profile):
        """
        This function wrap the send_activation_email() function call.
        Feel free the overload this function to change the email settings.
        """
        profile.send_activation_email(subject_template_name='registration/activate_user_email_subject.txt',
                                      email_template_name='registration/activate_user_email.txt',
                                      html_email_template_name='registration/activate_user_email.html',
                                      use_https=request.is_secure(),
                                      request=request)

    def delete_expired_users(self, request, queryset):
        """
        Delete the selected user registration profile.
        Note that this will *only* delete profile of users who have
        already used their activation key, or let them expired.
        Non expired registration profiles will NOT be deleted.
        :param request: Current request.
        :param queryset: Selected objects queryset.
        """
        UserRegistrationProfile.objects.delete_expired_users(queryset)
        self.message_user(request, _('Successfully deleted expired registrations in selection.'))
    delete_expired_users.short_description = _("Delete expired registrations")


admin.site.register(BannedUsername)
admin.site.register(BannedEmail)
admin.site.register(UserRegistrationProfile, RegistrationAdmin)
