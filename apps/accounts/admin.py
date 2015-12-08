"""
Admin views for the user accounts app.
"""

from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _

from .models import UserProfile
from .settings import NO_AVATAR_STATIC_URL


class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin page for the ``UserProfile`` model.
    """

    list_select_related = ('user', )

    list_display = ('avatar_img',
                    'user_username',
                    'last_modification_date',
                    'last_login_date',
                    'last_activity_date',
                    'is_online',
                    'related_user_admin_page_link',
                    'view_profile_on_site_link')

    list_display_links = ('avatar_img',
                          'user_username')

    list_filter = ('gender',
                   'first_last_names_public',
                   'email_public',
                   'search_by_email_allowed',
                   'online_status_public',
                   'accept_newsletter',
                   'last_modification_date',
                   'last_activity_date',
                   'user__last_login')

    search_fields = ('user__email',
                     'user__username',
                     'country',
                     'timezone',
                     'preferred_language',
                     'location',
                     'company',
                     'biography',
                     'signature',
                     'website_name',
                     'website_url',
                     'jabber_name',
                     'skype_name',
                     'twitter_name',
                     'facebook_url',
                     'googleplus_url',
                     'youtube_url',
                     'last_login_ip_address')

    readonly_fields = ('avatar_img',
                       'last_login_ip_address',
                       'last_modification_date',
                       'last_activity_date',
                       'last_login_date',
                       'is_online')

    fieldsets = (
        (_('Avatar'), {
            'fields': ('avatar_img',
                       'avatar')
        }),
        (_('General preferences'), {
            'fields': ('timezone',
                       'preferred_language',
                       'country')
        }),
        (_('Privacy preferences'), {
            'fields': ('first_last_names_public',
                       'email_public',
                       'search_by_email_allowed',
                       'online_status_public',
                       'accept_newsletter')
        }),
        (_('Personal information'), {
            'fields': ('gender',
                       'location',
                       'company',
                       'biography',
                       'signature')
        }),
        (_('Social network information'), {
            'fields': ('website_name',
                       'website_url',
                       'jabber_name',
                       'skype_name',
                       'twitter_name',
                       'facebook_url',
                       'googleplus_url',
                       'youtube_url')
        }),
        (_('Other information'), {
            'fields': ('last_modification_date',
                       'last_activity_date',
                       'is_online',
                       'last_login_date',
                       'last_login_ip_address')
        }),
    )

    def user_username(self, obj):
        """
        Return the username of the related user.
        :param obj: Current model object.
        """
        return obj.user.username
    user_username.short_description = _('Related user')
    user_username.admin_order_field = 'user__username'

    def avatar_img(self, obj):
        """
        Return the current user's avatar image as html ``<img>`` tag for the admin edit view.
        :param obj: Current model object.
        """
        return '<img src="%s" />' % (obj.avatar.url if obj.avatar else static(NO_AVATAR_STATIC_URL))
    avatar_img.short_description = _('Current avatar')
    avatar_img.allow_tags = True

    def last_login_date(self, obj):
        """
        Return the last login date of the related user.
        :param obj: Current model object.
        """
        return obj.user.last_login
    last_login_date.short_description = _('Last login date')
    last_login_date.admin_order_field = 'user__last_login'

    def related_user_admin_page_link(self, obj):
        """
        Return a link to the related user admin edit page.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=[obj.user.pk]), _('Edit raw user'))
    related_user_admin_page_link.short_description = ''
    related_user_admin_page_link.allow_tags = True

    def view_profile_on_site_link(self, obj):
        """
        Return a link to the user's public profile.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (obj.get_absolute_url(), _('View on site'))
    view_profile_on_site_link.short_description = ''
    view_profile_on_site_link.allow_tags = True


admin.site.register(UserProfile, UserProfileAdmin)
