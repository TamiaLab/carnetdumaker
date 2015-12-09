"""
Views for the announcements app.
"""

from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .settings import NB_ANNOUNCEMENTS_PER_PAGE
from .models import (Announcement,
                     AnnouncementTag)


def announcement_list(request,
                      template_name='announcements/announcement_list.html',
                      extra_context=None):
    """
    Announcements list view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all published announcements
    published_announcements = Announcement.objects.published() \
        .select_related('author').prefetch_related('tags')

    # Announcements list pagination
    paginator, page = paginate(published_announcements, request, NB_ANNOUNCEMENTS_PER_PAGE)

    # Render the template
    context = {
        'title': _('Announcements list'),
    }
    update_context_for_pagination(context, 'announcements', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def announcement_detail(request, slug,
                        template_name='announcements/announcement_detail.html',
                        extra_context=None):
    """
    Detail view for a specific announcement.
    :param slug: The desired announcement's slug.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve the announcement
    manager = Announcement.objects.select_related('author', 'author__user_profile').prefetch_related('tags')
    announcement_obj = get_object_or_404(manager, slug=slug)

    # Check for preview
    if not announcement_obj.is_published() and \
            not announcement_obj.can_see_preview(request.user):
        raise Http404()

    # Render the template
    context = {
        'announcement': announcement_obj,
        'title': announcement_obj.title,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def tag_list(request,
             template_name='announcements/tag_list.html',
             extra_context=None):
    """
    List view of all tags as a "cloud".
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all tag to create a freaking awesome tag cloud
    queryset = AnnouncementTag.objects.all()

    # Render the template without pagination
    context = {
        'title': _('Tags list'),
        'tags': queryset,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def tag_detail(request, slug,
               template_name='announcements/tag_detail.html',
               extra_context=None):
    """
    Detail view for a specific tag.
    :param slug: The desired tag's slug.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve the tag
    tag_obj = get_object_or_404(AnnouncementTag, slug=slug)

    # Related announcements list pagination
    paginator, page = paginate(tag_obj.announcements.published()
                               .select_related('author').prefetch_related('tags'),
                               request, NB_ANNOUNCEMENTS_PER_PAGE)

    # Render the template
    context = {
        'title': _('Tag %s') % tag_obj.name,
        'tag': tag_obj,
    }
    update_context_for_pagination(context, 'related_announcements', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
