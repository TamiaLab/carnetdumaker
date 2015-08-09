"""
Admin views for the forum app.
"""

from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from apps.tools.http_utils import get_client_ip_address

from .models import (Forum,
                     ForumThread,
                     ForumThreadPost,
                     ForumSubscription,
                     ForumThreadSubscription,
                     ReadForumTracker,
                     ReadForumThreadTracker,
                     ForumUserProfile)
from .notifications import (notify_of_new_forum_thread,
                            notify_of_new_thread_post)


class ForumThreadPostAdmin(admin.ModelAdmin):
    """
    Forum's thread's post admin form.
    """

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Overload to pre-fill initial author with the current user PK.
        :param db_field: The current db field.
        :param request: The current request.
        :param kwargs: Extra named parameters.
        :return: super() result.
        """
        if db_field.name == 'author':
            kwargs['initial'] = request.user.id
        return super(ForumThreadPostAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_select_related = ('author',
                           'parent_thread',
                           'last_modification_by')

    list_display = ('post_id',
                    'author_username_link',
                    'parent_thread_link',
                    'pub_date',
                    'last_modification_date',
                    'last_modification_by',
                    'is_deleted')

    readonly_fields = ('pub_date',
                       'last_modification_date',
                       'last_modification_by',
                       'author_ip_address')

    list_filter = ('pub_date',
                   'last_modification_date',
                   'deleted_at')

    search_fields = ('id',
                     'parent_thread__id'
                     'parent_thread__title'
                     'author__email',
                     'author__username',
                     'content',
                     'author_ip_address')

    raw_id_fields = ('author',
                     'last_modification_by',
                     'parent_thread')

    fieldsets = (
        (_('System information'), {
            'fields': ('parent_thread',)
        }),
        (_('Post information'), {
            'fields': ('author',
                       'pub_date',
                       'content')
        }),
        (_('Date and time'), {
            'fields': ('last_modification_date',
                       'last_modification_by',
                       'deleted_at')
        }),
        (_('Legal stuff'), {
            'fields': ('author_ip_address',)
        }),
    )

    def post_id(self, obj):
        """
        Return the post ID in #ID format.
        :param obj: Current post object.
        :return: The post ID in #ID format.
        """
        return '#%d' % obj.id if obj.id else None
    post_id.short_description = _('ID')
    post_id.admin_order_field = 'id'

    def parent_thread_link(self, obj):
        """
        Return a link to the parent thread.
        :param obj: Current post object.
        :return: HTML <a> link.
        """
        parent_thread = obj.parent_thread
        if parent_thread is None:
            return ''
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:forum_forumthread_change', args=[parent_thread.pk]),
                           parent_thread.title)
    parent_thread_link.short_description = _('Parent thread')
    parent_thread_link.admin_order_field = 'parent_thread__title'
    parent_thread_link.allow_tags = True

    def author_username_link(self, obj):
        """
        Return a link to the author.
        :param obj: Current post object.
        :return: HTML <a> link.
        """
        author = obj.author
        if author is None:
            return ''
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:auth_user_change', args=[author.pk]),
                           author.username)
    author_username_link.short_description = _('Author')
    author_username_link.admin_order_field = 'author__username'
    author_username_link.allow_tags = True


class ForumThreadPostInline(admin.StackedInline):
    """
    Forum's thread's post inline admin form.
    """

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Overload to pre-fill initial author with the current user PK.
        :param db_field: The current db field.
        :param request: The current request.
        :param kwargs: Extra named parameters.
        :return: super() result.
        """
        if db_field.name == 'author':
            kwargs['initial'] = request.user.id
        return super(ForumThreadPostInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """
        Return the queryset for this inline form.
        """
        # TODO SEEM TO BE NOT WORKING
        return super(ForumThreadPostInline, self).get_queryset(request) \
            .select_related('author', 'last_modification_by', )

    model = ForumThreadPost

    readonly_fields = ('pub_date',
                       'last_modification_date',
                       'last_modification_by',
                       'author_ip_address')

    raw_id_fields = ('author',
                     'last_modification_by',
                     'parent_thread')

    extra = 1

    fieldsets = (
        (_('System information'), {
            'fields': ('parent_thread',)
        }),
        (_('Post information'), {
            'fields': ('author',
                       'pub_date',
                       'content')
        }),
        (_('Date and time'), {
            'fields': ('last_modification_date',
                       'last_modification_by',
                       'deleted_at')
        }),
        (_('Legal stuff'), {
            'fields': ('author_ip_address',)
        }),
    )


def view_issue_on_site(obj):
    """
    Simple "view on site" inline callback.
    :param obj: Current database object.
    :return: HTML <a> link to the given object.
    """
    return format_html('<a href="{0}" class="link">{1}</a>',
                       obj.get_absolute_url(),
                       _('View on site'))
view_issue_on_site.short_description = ''
view_issue_on_site.allow_tags = True


class ForumThreadAdmin(admin.ModelAdmin):
    """
    ``ForumThread`` admin form.
    """

    def save_formset(self, request, form, formset, change):
        """
        Save inline forms (used for posts). Fix user's IP address on save() and notify
        subscribers of new post.
        :param request: The current request.
        :param form: The form instance.
        :param formset: The formset instance.
        :param change: True if form data has changed.
        :return: None
        """

        # Overload save method for inline posts
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:

            # Update IP address field if new object
            if not instance.pk:
                just_created = True
                instance.author_ip_address = get_client_ip_address(request)
            else:
                just_created = False

            # Save the model
            instance.save(current_user=request.user)

            # Notify subscribers of new comment
            if just_created:
                notify_of_new_thread_post(instance, request, instance.author)

        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        """
        Save the model. Notify subscribers of new thread.
        :param request: The current request.
        :param obj: The current object to be saved.
        :param form: The parent form instance.
        :param change: True if form data has changed.
        :return: None
        """

        # Detect new thread
        just_created = obj.pk is None

        # Save the model
        obj.save()

        # Notify subscribers of new thread
        if just_created:
            notify_of_new_forum_thread(obj, request, obj.first_post.author)

    def get_readonly_fields(self, request, obj=None):
        """
        Get all readonly fields.
        :param request: The current request.
        :param obj: The object being edited.
        :return: None
        """
        if obj:  # Editing
            return self.readonly_fields + (
                'first_post',
                'last_post'
            )
        return self.readonly_fields

    list_select_related = ('parent_forum',
                           'first_post',
                           'last_post',
                           'first_post__author',
                           'first_post__last_modification_by')

    list_display = ('thread_id',
                    'title',
                    'parent_forum_link',
                    'author_username_link',
                    'sticky',
                    'global_sticky',
                    'closed',
                    'resolved',
                    'locked',
                    view_issue_on_site)

    list_display_links = ('thread_id',
                          'title')

    list_filter = ('sticky',
                   'global_sticky',
                   'closed',
                   'resolved',
                   'locked',
                   'parent_forum')

    search_fields = ('id',
                     'title',
                     'first_post__author__email',
                     'first_post__author__username')

    readonly_fields = ('parent_forum_link',
                       'author_username_link')

    raw_id_fields = ('parent_forum',
                     'first_post',
                     'last_post')

    fieldsets = (
        (_('Thread information'), {
            'fields': ('title',
                       'parent_forum')
        }),
        (_('Thread status'), {
            'fields': ('sticky',
                       'global_sticky',
                       'closed',
                       'resolved',
                       'locked')
        }),
        (_('First and last post'), {
            'fields': ('first_post',
                       'last_post')
        }),
    )

    inlines = (ForumThreadPostInline,)

    def thread_id(self, obj):
        """
        Return the thread ID in #ID format.
        :param obj: Current thread object.
        :return: The thread ID in #ID format.
        """
        return '#%d' % obj.id if obj.id else None
    thread_id.short_description = _('ID')
    thread_id.admin_order_field = 'id'

    def parent_forum_link(self, obj):
        """
        Return a HTML link to the parent forum's admin page.
        :param obj: The current Revision object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:forum_forum_change', args=[obj.parent_forum.pk]),
                                        obj.parent_forum.slug_hierarchy) if obj.parent_forum.pk else ''
    parent_forum_link.short_description = ''
    parent_forum_link.allow_tags = True

    def author_username_link(self, obj):
        """
        Return a link to the author.
        :param obj: Current post object.
        :return: HTML <a> link.
        """
        author = obj.first_post.author
        if author is None:
            return ''
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:auth_user_change', args=[author.pk]),
                           author.username)
    author_username_link.short_description = _('Author')
    author_username_link.admin_order_field = 'first_post__author__username'
    author_username_link.allow_tags = True


class ForumThreadLinkInline(admin.TabularInline):
    """
    Forum's thread simple links inline admin form.
    """

    model = ForumThread

    extra = 0

    max_num = 0

    fields = ('title',
              'sticky',
              'global_sticky',
              'closed',
              'resolved',
              'locked',
              'thread_admin_link')
    readonly_fields = fields

    def thread_admin_link(self, obj):
        """
        Return a HTML link to the thread's admin page.
        :param obj: The current Revision object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:forum_forumthread_change', args=[obj.pk]),
                                        _('Edit thread in admin')) if obj.pk else ''
    thread_admin_link.short_description = ''
    thread_admin_link.allow_tags = True


class ChildForumLinkInline(admin.TabularInline):
    """
    Child forum simple links inline admin form.
    """

    model = Forum

    extra = 0

    max_num = 0

    fields = ('title',
              'private',
              'closed',
              'ordering',
              'forum_admin_link')
    readonly_fields = fields

    def forum_admin_link(self, obj):
        """
        Return a HTML link to the forum's admin page.
        :param obj: The current Revision object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:forum_forum_change', args=[obj.pk]),
                                        _('Edit forum in admin')) if obj.pk else ''
    forum_admin_link.short_description = ''
    forum_admin_link.allow_tags = True


class ForumAdminForm(forms.ModelForm):
    """
    Custom admin model form with extra checkbox for set_close / set_private routines.
    """

    close_child_threads = forms.BooleanField(label=_('Close child threads'),
                                             required=False,
                                             initial=False)

    close_recursive = forms.BooleanField(label=_('Close sub-forums recursively'),
                                         required=False,
                                         initial=False)

    private_recursive = forms.BooleanField(label=_('Set sub-forums as private recursively'),
                                           required=False,
                                           initial=False)

    class Meta:
        model = Forum
        fields = '__all__'

    def save(self, commit=True):
        """
        Custom save method with set_closed() and set_private() support.
        """
        self.instance.set_closed(self.cleaned_data['closed'],
                                 self.cleaned_data['close_child_threads'],
                                 self.cleaned_data['close_recursive'])
        self.instance.set_private(self.cleaned_data['private'],
                                  self.cleaned_data['private_recursive'])
        return super(ForumAdminForm, self).save(commit=commit)


class ForumAdmin(admin.ModelAdmin):
    """
    ``Forum`` admin form.
    """

    form = ForumAdminForm

    list_display = ('logo_img',
                    'slug_hierarchy',
                    'title',
                    'private',
                    'closed',
                    'ordering',
                    view_issue_on_site)

    list_display_links = ('logo_img',
                          'slug_hierarchy',
                          'title')

    readonly_fields = ('logo_img',
                       'slug_hierarchy')

    list_filter = ('private',
                   'closed')

    search_fields = ('title',
                     'description')

    prepopulated_fields = {'slug': ('title',)}

    raw_id_fields = ('parent',)

    fieldsets = (
        (_('Forum information'), {
            'fields': ('title',
                       'slug',
                       'logo',
                       'description')
        }),
        (_('Forum status'), {
            'fields': ('private',
                       'private_recursive',
                       'closed',
                       'close_child_threads',
                       'close_recursive')
        }),
        (_('Other stuff'), {
            'fields': ('parent',
                       'ordering')
        }),
    )

    inlines = (ChildForumLinkInline, ForumThreadLinkInline)

    def logo_img(self, obj):
        """
        Return the forum's logo image as html ``<img>`` tag for the admin edit view.
        :param obj: Current model object.
        """
        return '<img src="%s" />' % obj.logo.url if obj.logo else ''
    logo_img.short_description = _('Logo')
    logo_img.allow_tags = True


class ForumUserProfileAdmin(admin.ModelAdmin):
    """
    ``ForumUserProfile`` admin form.
    """

    list_select_related = ('user',)

    list_display = ('user_username',
                    'notify_of_reply_by_default',
                    'last_post_date')

    list_filter = ('notify_of_reply_by_default',
                   'last_post_date')

    search_fields = ('user__email',
                     'user__username')

    readonly_fields = ('user_username',)

    fields = ('user_username',
              'notify_of_reply_by_default',
              'last_post_date')

    def user_username(self, obj):
        """
        Return the related user's username.
        :param obj: Current ticket object.
        :return: Relate user's username.
        """
        return obj.user.username
    user_username.short_description = _('Related user')
    user_username.admin_order_field = 'user__username'


admin.site.register(Forum, ForumAdmin)
admin.site.register(ForumThread, ForumThreadAdmin)
admin.site.register(ForumThreadPost, ForumThreadPostAdmin)
admin.site.register(ForumUserProfile, ForumUserProfileAdmin)

admin.site.register(ReadForumTracker)  # TODO make custom admin
admin.site.register(ReadForumThreadTracker)  # TODO make custom admin
admin.site.register(ForumSubscription)  # TODO make custom admin
admin.site.register(ForumThreadSubscription)  # TODO make custom admin
