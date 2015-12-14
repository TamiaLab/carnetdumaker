"""
Views for the image attachments app.
"""

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .models import ImageAttachment
from .settings import NB_IMG_ATTACHMENTS_PER_PAGE


def image_attachment_list(request,
                          template_name='imageattachments/image_attachment_list.html',
                          extra_context=None):
    """
    List all recently published image attachments.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all published image attachments
    published_images = ImageAttachment.objects.published_public().select_related('license')

    # Images list pagination
    paginator, page = paginate(published_images, request, NB_IMG_ATTACHMENTS_PER_PAGE)

    # Render the template
    context = {
        'title': _('Image attachments'),
    }
    update_context_for_pagination(context, 'images', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def image_attachment_detail(request, slug,
                            template_name='imageattachments/image_attachment_detail.html',
                            extra_context=None):
    """
    Detail view for a specific image attachment.
    :param slug: The desired image attachment's slug.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve the image
    manager = ImageAttachment.objects.published().select_related('license')
    image_obj = get_object_or_404(manager, slug=slug)

    # Render the template
    context = {
        'title': _('Image %s') % image_obj.title,
        'image': image_obj,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
