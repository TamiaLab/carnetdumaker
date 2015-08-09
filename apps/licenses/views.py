"""
Views for the licenses app.
"""

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .settings import NB_LICENSES_PER_PAGE
from .models import License


def license_list(request,
                 template_name='licenses/license_list.html',
                 extra_context=None):
    """
    List view of all licenses.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all licenses
    queryset = License.objects.all()

    # Licenses list pagination
    paginator, page = paginate(queryset, request, NB_LICENSES_PER_PAGE)

    # Render the template
    context = {
        'title': _('Licenses list'),
    }
    update_context_for_pagination(context, 'licenses', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def license_detail(request, slug,
                   template_name='licenses/license_detail.html',
                   extra_context=None):
    """
    Detail view for a specific license.
    :param slug: The desired license slug.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve the license
    license_obj = get_object_or_404(License, slug=slug)

    # Render the template
    context = {
        'title': _('License %s') % license_obj.name,
        'license': license_obj,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
