"""
Views for the code snippets app.
"""

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.http.response import HttpResponse

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .models import CodeSnippet
from .settings import NB_SNIPPETS_PER_PAGE


def snippet_list(request,
                 template_name='snippets/snippet_list.html',
                 extra_context=None):
    """
    Code snippets list view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all published code snippets
    published_snippets = CodeSnippet.objects.public_snippets().select_related('author')

    # Code snippets list pagination
    paginator, page = paginate(published_snippets, request, NB_SNIPPETS_PER_PAGE)

    # Render the template
    context = {
        'title': _('Code snippets list'),
    }
    update_context_for_pagination(context, 'snippets', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def snippet_detail(request, pk,
                   template_name='snippets/snippet_detail.html',
                   extra_context=None):
    """
    Detail view for a specific code snippet.
    :param pk: The desired code snippet's PK.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve the snippet
    manager = CodeSnippet.objects.select_related('author')
    snippet_obj = get_object_or_404(manager, pk=pk)

    # Render the template
    context = {
        'snippet': snippet_obj,
        'title': snippet_obj.title,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def snippet_raw(request, pk, download=False):
    """
    Raw source code view for a specific code snippet.
    :param pk: The desired code snippet's PK.
    :param download: Set to true to force the download of the file.
    :param request: The incoming request.
    :return: HttpResponse
    """

    # Retrieve the snippet
    snippet_obj = get_object_or_404(CodeSnippet, pk=pk)

    # Return the raw snippet source code
    source_code = snippet_obj.source_code
    response = HttpResponse(source_code, content_type='text/plain')
    response['Content-Length'] = len(source_code)
    if download:
        response['Content-Disposition'] = 'attachment; filename="%s"' % snippet_obj.filename
    response['X-Content-Type-Options'] = 'nosniff'
    return response
