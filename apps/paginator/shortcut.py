"""
Shortcut functions for pagination.
"""

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage


def get_page_number(request):
    """
    Return the page number from the given request using the ``page`` GET parameter.
    :param request: The current request.
    :return: The page number, or 1 if not specified.
    """
    return request.GET.get('page', None) or 1


def paginate(queryset, request, nb_objects_per_page=25):
    """
    Paginate the given queryset. Raise Http404 on invalid page number.
    :param queryset: The queryset to be paginated.
    :param request: The current request (for retrieving the page number).
    :param nb_objects_per_page: The number of objects per page.
    :return: A tuple of (paginator, page) objects.
    """
    page_number = get_page_number(request)
    paginator = Paginator(queryset, nb_objects_per_page)
    try:
        page = paginator.page(page_number)
    except InvalidPage as e:
        raise Http404(_('Invalid page number (%(page_number)s): %(message)s') % {
            'page_number': page_number,
            'message': str(e)
        })
    return paginator, page


def update_context_for_pagination(context, object_list_name, request, paginator, page):
    """
    Update the given context for pagination using the given paginator and page objects.
    :param context: The context to be updated.
    :param object_list_name: The name of the context variable for the object list of the current page.
    :param request: The current request (used to keep GET parameters in pagination links).
    :param paginator: The source paginator object.
    :param page: The source page object.
    :return: None
    """
    get_params = request.GET.copy()
    if 'page' in get_params:
        get_params.pop('page')
    if get_params:
        get_params = get_params.urlencode()
    else:
        get_params = ''
    paginator_context = {
        'paginator': paginator,
        'page_obj': page,
        'is_first_page': page.number == 1,
        'is_paginated': page.has_other_pages(),
        object_list_name: page.object_list,
        'get_params': get_params,
        'get_params_union': '&%s' % get_params if get_params else '',
        }
    context.update(paginator_context)
