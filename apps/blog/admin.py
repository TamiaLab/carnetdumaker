"""
Admin views for the blog app.
"""

import difflib

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from .models import (Article,
                     ArticleRevision,
                     ArticleNote,
                     ArticleTag,
                     ArticleCategory)


class ArticleRevisionInline(admin.TabularInline):
    """
    Article's revision inline admin form.
    """

    def get_queryset(self, request):
        """
        Return the queryset for this inline form. Prefetch related author.
        :param request: The current request.
        """
        return super(ArticleRevisionInline, self).get_queryset(request) \
            .select_related('revision_author')

    model = ArticleRevision

    extra = 0

    max_num = 0

    fields = ('revision_date',
              'revision_author_username_link',
              'revision_minor_change',
              'revision_description',
              'show_diff_with_current_version')
    readonly_fields = fields

    def revision_author_username_link(self, obj):
        """
        Return the username of the related revision's author as a link to the related user admin edit page.
        :param obj: Current model object.
        """
        if obj.revision_author is None:
            return ''
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change',
                                                args=[obj.revision_author.pk]),
                                        obj.revision_author.username)
    revision_author_username_link.short_description = _('Revision author')
    revision_author_username_link.admin_order_field = 'revision_author__username'
    revision_author_username_link.allow_tags = True

    def show_diff_with_current_version(self, obj):
        """
        Return a HTML link to the revision diff view.
        :param obj: The current Revision object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:blog_article_show_rev_diff', args=[obj.pk]),
                                        _('Show diff with current version')) if obj.pk else ''
    show_diff_with_current_version.short_description = _('Show diff with current version')
    show_diff_with_current_version.allow_tags = True


class ArticleAdminForm(forms.ModelForm):
    """
    Custom admin model form with extra checkbox for minor_change routine.
    """

    minor_change = forms.BooleanField(label=_('Minor changes'),
                                      required=False,
                                      initial=False)

    revision_description = forms.CharField(widget=forms.Textarea(),
                                           label=_('Revision description'),
                                           required=False,
                                           initial='')

    class Meta:
        model = Article
        fields = '__all__'


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


class ArticleAdmin(admin.ModelAdmin):
    """
    Blog article admin form.
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
        return super(ArticleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Save the data model, create revision using the current user PK.
        :param request: The current request.
        :param obj: The current object ot be saved.
        :param form: The modification form instance.
        :param change: Not used.
        :return: None
        """
        minor_change = form.cleaned_data['minor_change']
        revision_description = form.cleaned_data['revision_description']
        obj.save(current_user=request.user,
                 minor_change=minor_change,
                 revision_description=revision_description)

    def get_urls(self):
        """
        Overload admin view urls for the "show revision diff" view.
        :return:
        """
        urls = super(ArticleAdmin, self).get_urls()
        my_urls = [
            url(r'^show_rev_diff/(?P<revision_pk>[0-9]+)/$',
                self.admin_site.admin_view(self.show_rev_diff),
                name='blog_article_show_rev_diff'),
        ]
        return my_urls + urls

    def show_rev_diff(self, request, revision_pk):
        """
        Show a diff table between the current article and the given revision.
        :param request: The current request.
        :param revision_pk: The desired revision PK.
        :return: TemplateResponse
        """

        # Get the article and his revision
        revision_obj = get_object_or_404(ArticleRevision, pk=revision_pk)
        article_obj = revision_obj.related_article

        # Compute the diff
        title_diff = '\n'.join(difflib.ndiff([revision_obj.title], [article_obj.title]))
        subtitle_diff = '\n'.join(difflib.ndiff([revision_obj.subtitle], [article_obj.subtitle]))
        description_diff = '\n'.join(
            difflib.ndiff(revision_obj.description.splitlines(), article_obj.description.splitlines()))
        content_diff = '\n'.join(difflib.ndiff(revision_obj.content.splitlines(), article_obj.content.splitlines()))

        # Render the template
        context = {
            # Translators: This message appears in the title of the article's revision diff view
            'title': _('Revision diff'),
            'article': article_obj,
            'revision': revision_obj,
            'title_diff_html': title_diff,
            'subtitle_diff_html': subtitle_diff,
            'content_diff_html': content_diff,
            'description_diff_html': description_diff
        }

        # Include common variables for rendering the admin template.
        context.update(self.admin_site.each_context(request))
        return TemplateResponse(request, "blog/admin_show_rev_diff.html", context)

    form = ArticleAdminForm

    list_select_related = ('author',
                           'license')

    list_display = ('title',
                    'author_username_link',
                    'creation_date',
                    'pub_date',
                    'status',
                    'featured',
                    'membership_required',
                    'require_membership_for_reading',
                    'is_published',
                    'is_gone',
                    view_issue_on_site)

    list_filter = ('status',
                   'creation_date',
                   'last_content_modification_date',
                   'pub_date',
                   'expiration_date',
                   'membership_required',
                   'membership_required_expiration_date',
                   'featured',
                   'network_publish',
                   'auto_create_related_forum_thread',
                   'display_img_gallery')

    search_fields = ('title',
                     'subtitle',
                     'license_name',
                     'author__username',
                     'author__email',
                     'description',
                     'content')

    readonly_fields = ('creation_date',
                       'last_content_modification_date',
                       'author_username_link',
                       'require_membership_for_reading',
                       'is_published',
                       'is_gone',
                       'cur_heading_img',
                       'cur_thumbnail_img')

    prepopulated_fields = {'slug': ('title',)}

    raw_id_fields = ('author',
                     'license',
                     'related_forum_thread')

    fieldsets = (
        (_('Title and subtitle'), {
            'fields': ('title',
                       'slug',
                       'subtitle')
        }),
        (_('Iconography'), {
            'fields': ('cur_heading_img',
                       'heading_img',
                       'cur_thumbnail_img',
                       'thumbnail_img')
        }),
        (_('Content'), {
            'fields': ('author',
                       'description',
                       'content')
        }),
        (_('Revision information'), {
            'fields': ('minor_change',
                       'revision_description')
        }),
        (_('General information'), {
            'fields': ('status',
                       'license',
                       'network_publish',
                       'featured')
        }),
        (_('Date and time'), {
            'fields': ('creation_date',
                       'last_content_modification_date',
                       'pub_date',
                       'expiration_date')
        }),
        (_('Membership'), {
            'fields': ('membership_required',
                       'membership_required_expiration_date')
        }),
        (_('Related forum thread'), {
            'fields': ('related_forum_thread',
                       'auto_create_related_forum_thread')
        }),
        (_('Tags, attachments and categories'), {
            'fields': ('tags',
                       'categories',
                       'img_attachments',
                       'display_img_gallery')
        }),
        (_('Related articles'), {
            'fields': ('follow_up_of',
                       'related_articles')
        }),
        (_('Notes and disclaimers'), {
            'fields': ('head_notes',
                       'foot_notes')
        }),
    )

    filter_horizontal = ('tags',
                         'categories',
                         'img_attachments',
                         'follow_up_of',
                         'related_articles',
                         'head_notes',
                         'foot_notes')

    inlines = (ArticleRevisionInline,)

    def author_username_link(self, obj):
        """
        Return the username of the related article's author as a link to the related user admin edit page.
        :param obj: Current model object.
        """
        return '<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=[obj.author.pk]), obj.author.username)
    author_username_link.short_description = _('Author')
    author_username_link.admin_order_field = 'author__username'
    author_username_link.allow_tags = True

    def cur_heading_img(self, obj):
        """
        Return the current heading image as html ``<img>`` tag for the admin edit view.
        :param obj: Current model object.
        """
        return '<img src="%s" />' % obj.heading_img.url if obj.heading_img else ''
    cur_heading_img.short_description = _('Current heading image')
    cur_heading_img.allow_tags = True

    def cur_thumbnail_img(self, obj):
        """
        Return the current thumbnail image as html ``<img>`` tag for the admin edit view.
        :param obj: Current model object.
        """
        return '<img src="%s" />' % obj.thumbnail_img.url if obj.thumbnail_img else ''
    cur_thumbnail_img.short_description = _('Current thumbnail image')
    cur_thumbnail_img.allow_tags = True


class ArticleNoteAdmin(admin.ModelAdmin):
    """
    Blog article note admin form.
    """

    list_display = ('title_internal',
                    'title',
                    'type')

    list_filter = ('type',)

    search_fields = ('title_internal',
                     'title',
                     'description')

    fieldsets = (
        (_('Internal information'), {
            'fields': ('title_internal',
                       'type')
        }),
        (_('Note content'), {
            'fields': ('title',
                       'description')
        }),
    )


class ArticleTagAdmin(admin.ModelAdmin):
    """
    Blog article tag admin form.
    """

    list_display = ('name',
                    'tag_use_count',
                    view_issue_on_site)

    search_fields = ('name',
                     'slug')

    readonly_fields = ('tag_use_count',)

    prepopulated_fields = {'slug': ('name',)}

    fields = ('name',
              'slug',
              'tag_use_count')

    def tag_use_count(self, obj):
        """
        Return the number of article using this tag.
        :param obj: Current model object.
        """
        return obj.use_count
    tag_use_count.short_description = _('Use count')

    def get_queryset(self, request):
        """
        Return the queryset, with count annotation.
        :param request: The current request.
        """
        return super(ArticleTagAdmin, self).get_queryset(request) \
            .annotate(use_count=Count('articles'))


class ArticleCategoryAdmin(admin.ModelAdmin):
    """
    Blog article category admin form.
    """

    list_display = ('logo_img',
                    'name',
                    'slug_hierarchy',
                    view_issue_on_site)

    list_display_links = ('logo_img',
                          'name')

    search_fields = ('name',
                     'slug',
                     'description')

    readonly_fields = ('slug_hierarchy',
                       'logo_img')

    prepopulated_fields = {'slug': ('name',)}

    raw_id_fields = ('parent',)

    fieldsets = (
        (_('Category name and parent'), {
            'fields': ('name',
                       'slug',
                       'parent')
        }),
        (_('Iconography'), {
            'fields': ('logo_img',
                       'logo')
        }),
        ('Category description', {
            'fields': ('description',)
        }),
    )

    def logo_img(self, obj):
        """
        Return the current logo image as html ``<img>``.
        :param obj: Current model object.
        """
        return '<img src="%s" />' % obj.logo.url if obj.logo else ''
    logo_img.short_description = _('Logo')
    logo_img.allow_tags = True


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleNote, ArticleNoteAdmin)
admin.site.register(ArticleTag, ArticleTagAdmin)
admin.site.register(ArticleCategory, ArticleCategoryAdmin)
