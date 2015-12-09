"""
Admin views for the announcements app.
"""

from django.contrib import admin
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import (Announcement,
                     AnnouncementTag,
                     AnnouncementTwitterCrossPublication)


def view_on_site(obj):
    """
    Simple "view on site" inline callback.
    :param obj: Current database object.
    :return: HTML <a> link to the given object.
    """
    return format_html('<a href="{0}" class="link">{1}</a>',
                       obj.get_absolute_url(),
                       _('View on site'))
view_on_site.short_description = ''
view_on_site.allow_tags = True


class AnnouncementAdmin(admin.ModelAdmin):
    """
    Admin panel for the ``Announcement`` model.
    """

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Overload to pre-fill initial author with the current user PK.
        :param db_field: The current db field.
        :param request: The current request.
        :param kwargs: Extra named parameters.
        :return: super() result.
        """
        if db_field.name == 'author' and request is not None:
            kwargs['initial'] = request.user.id
        return super(AnnouncementAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_select_related = ('author', )

    list_display = ('title',
                    'author_username_link',
                    'creation_date',
                    'last_content_modification_date',
                    'pub_date',
                    'type',
                    'site_wide',
                    view_on_site)

    list_filter = ('creation_date',
                   'last_content_modification_date',
                   'pub_date',
                   'type',
                   'site_wide')

    search_fields = ('title',
                     'author__username',
                     'author__email',
                     'content')

    raw_id_fields = ('author', )

    readonly_fields = ('author_username_link',
                       'creation_date',
                       'last_content_modification_date',
                       'last_modification_date')

    prepopulated_fields = {'slug': ('title', )}

    fieldsets = (
        (_('Title and slug'), {
            'fields': ('title',
                       'slug')
        }),
        (_('Content'), {
            'fields': ('author',
                       'type',
                       'site_wide',
                       'content',
                       'tags')
        }),
        (_('Date and time'), {
            'fields': ('creation_date',
                       'pub_date',
                       'last_content_modification_date',
                       'last_modification_date')
        }),
    )

    filter_horizontal = ('tags', )

    def author_username_link(self, obj):
        """
        Return the username of the related announcement's author as a link to the related user admin edit page.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=[obj.author.pk]), obj.author.username)
    author_username_link.short_description = _('Author')
    author_username_link.admin_order_field = 'author__username'
    author_username_link.allow_tags = True


class AnnouncementTagAdmin(admin.ModelAdmin):
    """
    Admin panel for the ``AnnouncementTag`` model.
    """

    list_display = ('name',
                    'tag_use_count',
                    view_on_site)

    search_fields = ('name',
                     'slug')

    raw_id_fields = ('author', )

    readonly_fields = ('tag_use_count', )

    prepopulated_fields = {'slug': ('name', )}

    fields = ('name',
              'slug',
              'tag_use_count')

    def tag_use_count(self, obj):
        """
        Return the number of announcements using this tag.
        :param obj: Current model object.
        """
        return obj.use_count
    tag_use_count.short_description = _('Use count')

    def get_queryset(self, request):
        """
        Return the queryset, with count annotation.
        :param request: The current request.
        """
        return super(AnnouncementTagAdmin, self).get_queryset(request) \
            .annotate(use_count=Count('articles'))


class AnnouncementTwitterCrossPublicationAdmin(admin.ModelAdmin):
    """
    Admin panel for the ``AnnouncementTwitterCrossPublication`` model.
    """

    list_select_related = ('announcement', )

    list_display = ('announcement',
                    'tweet_id',
                    'pub_date',
                    'view_announcement_on_site',
                    'view_announcement_on_twitter')

    list_filter = ('pub_date', )

    search_fields = ('announcement__title',
                     'tweet_id')

    readonly_fields = ('pub_date', )

    fields = ('announcement',
              'tweet_id',
              'pub_date')

    def view_announcement_on_site(self, obj):
        """
        Inline list display link to view the announcement on the site.
        :param obj: the current object.
        :return: HTML <a> link to the given object on the site.
        """
        return format_html('<a href="{0}" class="link">{1}</a>',
                       obj.get_absolute_url(),
                       _('View announcement on site'))
    view_announcement_on_site.short_description = ''
    view_announcement_on_site.allow_tags = True

    def view_announcement_on_twitter(self, obj):
        """
        Inline list display link to view the announcement on Twitter.
        :param obj: the current object.
        :return: HTML <a> link to the given object on Twitter.
        """
        return format_html('<a href="https://twitter.com/redirect/status/{0}" class="link">{1}</a>',
                       obj.tweet_id,
                       _('View announcement on Twitter'))
    view_announcement_on_twitter.short_description = ''
    view_announcement_on_twitter.allow_tags = True


admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(AnnouncementTag, AnnouncementTagAdmin)
admin.site.register(AnnouncementTwitterCrossPublication, AnnouncementTwitterCrossPublicationAdmin)
