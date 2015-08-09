"""
Admin views for the bug tracker app.
"""

from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from apps.tools.http_utils import get_client_ip_address

from .models import (AppComponent,
                     IssueTicket,
                     IssueComment,
                     IssueChange,
                     IssueTicketSubscription,
                     BugTrackerUserProfile)
from .notifications import (notify_of_new_comment,
                            notify_of_new_issue)


class AppComponentAdmin(admin.ModelAdmin):
    """
    Admin form for the ``AppComponent`` data model.
    """

    list_display = ('name',
                    'internal_name',
                    'description')

    search_fields = ('name',
                     'internal_name',
                     'description')

    fieldsets = (
        (_('Component information'), {
            'fields': ('name',
                       'internal_name',
                       'description')
        }),
    )


class IssueChangesInline(admin.TabularInline):
    """
    Issue's changes inline admin form.
    """

    model = IssueChange

    fields = ('change_date',
              'field_name',
              'old_value',
              'new_value')

    readonly_fields = fields

    extra = 0

    max_num = 0


class IssueCommentAdmin(admin.ModelAdmin):
    """
    Admin form for the ``IssueComment`` data model.
    """

    list_select_related = ('author',
                           'issue')

    list_display = ('issue_id',
                    'author_username_link',
                    'pub_date',
                    'short_body')

    search_fields = ('issue__id',
                     'issue__title',
                     'author__email',
                     'author__username',
                     'body')

    readonly_fields = ('pub_date',
                       'issue')

    fieldsets = (
        (_('General information'), {
            'fields': ('issue',
                       'author',
                       'pub_date')
        }),
        (_('Comment text'), {
            'fields': ('body',
                       'author_ip_address')
        }),
    )

    inlines = (IssueChangesInline,)

    def issue_id(self, obj):
        """
        Return the issue ID in #ID format.
        :param obj: Current ticket comment object.
        :return: The issue ID in #ID format.
        """
        return '#%d' % obj.issue_id if obj.issue_id else None
    issue_id.short_description = _('ID')
    issue_id.admin_order_field = 'issue__id'

    def author_username_link(self, obj):
        """
        Return a link to the comment author.
        :param obj: Current ticket comment object.
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


class IssueCommentInline(admin.StackedInline):
    """
    Issue's comment inline admin form.
    """

    model = IssueComment

    fields = ('author',
              'pub_date',
              'body',
              'author_ip_address')

    readonly_fields = ('pub_date',
                       'author_ip_address')

    raw_id_fields = ('author',)

    extra = 1

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
        return super(IssueCommentInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


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


class IssueTicketAdminForm(forms.ModelForm):
    """
    Custom admin model form with extra field for the changes comment.
    """

    changes_comment = forms.CharField(widget=forms.Textarea(),
                                      label=_('Modification comment'),
                                      required=False,
                                      initial='')

    class Meta:
        model = IssueTicket
        fields = '__all__'


class IssueTicketAdmin(admin.ModelAdmin):
    """
    ``IssueTicket`` admin form.
    """

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """
        Overload to pre-fill initial author with the current user PK.
        :param db_field: The current db field.
        :param request: The current request.
        :param kwargs: Extra named parameters.
        :return: super() result.
        """
        if db_field.name == 'submitter':
            kwargs['initial'] = request.user.id
        return super(IssueTicketAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Save the model. Notify subscribers of new issue.
        :param request: The current request.
        :param obj: The model object.
        :param form: The parent form instance.
        :param change: True if the model is updated, not created.
        :return: None
        """

        # Get extra args
        changes_comment = form.cleaned_data['changes_comment']
        changes_author_ip_address = get_client_ip_address(request)
        changes_author = request.user

        # Update IP address field if new object
        if not change:
            obj.submitter_ip_address = get_client_ip_address(request)

        # Save the model
        obj.save(changes_comment=changes_comment,
                 changes_author=changes_author,
                 changes_author_ip_address=changes_author_ip_address,
                 request=request)

        # Notify subscribers of new issue
        if not change:
            notify_of_new_issue(obj, request, obj.submitter)

    def save_formset(self, request, form, formset, change):
        """
        Save the formset for the inline comments. Notify subscribers of new comment.
        :param request: The current request.
        :param form: The parent form instance.
        :param formset: The formset instance.
        :param change: True if the form has change.
        :return: None
        """

        # Overload save method for inline comments
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
            instance.save()

            # Notify subscribers of new comment
            if just_created:
                notify_of_new_comment(instance.issue, instance, request, instance.author)

        formset.save_m2m()

    form = IssueTicketAdminForm

    list_select_related = ('component',
                           'submitter',
                           'assigned_to')

    list_display = ('issue_id',
                    'title',
                    'component_name',
                    'submitter_username_link',
                    'submission_date',
                    'last_modification_date',
                    'status',
                    'priority',
                    'difficulty',
                    'assigned_to_username_link',
                    view_issue_on_site)

    list_display_links = ('issue_id',
                          'title')

    list_filter = ('submission_date',
                   'last_modification_date',
                   'status',
                   'priority',
                   'difficulty')

    search_fields = ('id',
                     'submitter__email',
                     'submitter__username',
                     'assigned_to__email',
                     'assigned_to__username',
                     'submitter_ip_address',
                     'description',
                     'title')

    readonly_fields = ('submitter_ip_address',
                       'submission_date',
                       'last_modification_date')

    raw_id_fields = ('submitter',
                     'assigned_to',
                     'component')

    fieldsets = (
        (_('Issue information'), {
            'fields': ('title',
                       'component',
                       'submitter',
                       'submitter_ip_address',
                       'description',
                       'changes_comment')
        }),
        (_('Issue date and time'), {
            'fields': ('submission_date',
                       'last_modification_date')
        }),
        (_('Issue status'), {
            'fields': ('status',
                       'priority',
                       'difficulty',
                       'assigned_to')
        }),
    )

    inlines = (IssueChangesInline, IssueCommentInline)

    def issue_id(self, obj):
        """
        Return the issue ID in #ID format.
        :param obj: Current ticket object.
        :return: The issue ID in #ID format.
        """
        return '#%d' % obj.id if obj.id else None
    issue_id.short_description = _('ID')
    issue_id.admin_order_field = 'id'

    def component_name(self, obj):
        """
        Return the related component name for the given ticket.
        :param obj: Current ticket object.
        :return: The related component name.
        """
        if not obj.component:
            return ''
        return obj.component.name
    component_name.short_description = _('Component')
    component_name.admin_order_field = 'component__name'

    def submitter_username_link(self, obj):
        """
        Return a link to the submitter.
        :param obj: Current ticket object.
        :return: HTML <a> link.
        """
        submitter = obj.submitter
        if submitter is None:
            return ''
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:auth_user_change', args=[submitter.pk]),
                           submitter.username)
    submitter_username_link.short_description = _('Submitter')
    submitter_username_link.admin_order_field = 'submitter__username'
    submitter_username_link.allow_tags = True

    def assigned_to_username_link(self, obj):
        """
        Return a link to the assigned to issue user.
        :param obj: Current ticket object.
        :return: HTML <a> link.
        """
        assigned_to = obj.assigned_to
        if assigned_to is None:
            return ''
        return format_html('<a href="{0}" class="link">{1}</a>',
                           reverse('admin:auth_user_change', args=[assigned_to.pk]),
                           assigned_to.username)
    assigned_to_username_link.short_description = _('Assigned to')
    assigned_to_username_link.admin_order_field = 'assign_to__username'
    assigned_to_username_link.allow_tags = True


class BugTrackerUserProfileAdmin(admin.ModelAdmin):
    """
    ``BugTrackerUserProfile`` admin form.
    """

    list_select_related = ('user',)

    list_display = ('user_username',
                    'notify_of_new_issue',
                    'notify_of_reply_by_default')

    list_filter = ('notify_of_new_issue',
                   'notify_of_reply_by_default',
                   'last_comment_date')

    search_fields = ('user__email',
                     'user__username')

    readonly_fields = ('user_username',)

    fields = ('user_username',
              'notify_of_new_issue',
              'notify_of_reply_by_default',
              'last_comment_date')

    def user_username(self, obj):
        """
        Return the related user's username.
        :param obj: Current ticket object.
        :return: Relate user's username.
        """
        return obj.user.username
    user_username.short_description = _('Related user')
    user_username.admin_order_field = 'user__username'


class IssueTicketSubscriptionAdmin(admin.ModelAdmin):
    """
    ``IssueTicketSubscription`` admin form.
    """

    list_select_related = ('user',
                           'issue')

    list_display = ('issue_title',
                    'user_username',
                    'active')

    search_fields = ('user__email',
                     'user__username',
                     'issue_id',
                     'issue__title')

    def issue_title(self, obj):
        """
        Return the related issue's issue.
        :param obj: Current ticket subscription object.
        :return: Relate issue's issue.
        """
        return obj.issue.title
    issue_title.short_description = _('Related issue')
    issue_title.admin_order_field = 'issue__title'

    def user_username(self, obj):
        """
        Return the related user's username.
        :param obj: Current ticket subscription object.
        :return: Relate user's username.
        """
        return obj.user.username
    user_username.short_description = _('Related user')
    user_username.admin_order_field = 'user__username'


admin.site.register(AppComponent, AppComponentAdmin)
admin.site.register(IssueTicket, IssueTicketAdmin)
admin.site.register(IssueComment, IssueCommentAdmin)
admin.site.register(BugTrackerUserProfile, BugTrackerUserProfileAdmin)
admin.site.register(IssueTicketSubscription, IssueTicketSubscriptionAdmin)
