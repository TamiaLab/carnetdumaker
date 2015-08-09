"""
Views for the content report app.
"""

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, resolve_url
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from .forms import ContentReportCreationForm


@never_cache
@csrf_protect
@login_required
def report_content(request, pk, objects_loader,
                   content_object_name='content_obj',
                   template_name='contentreport/content_report_form.html',
                   content_report_form=ContentReportCreationForm,
                   post_report_redirect=None,
                   extra_context=None):
    """
    View to report an inadequate content.
    :param request: The incoming request.
    :param pk: The comment PK to be reported.
    :param objects_loader: Manager class to be used to retrieve the content object.
    :param content_object_name: The context variable name to be used for the context object.
    :param template_name: The template to use for the view.
    :param content_report_form: The comment report form to be used.
    :param post_report_redirect: The post report redirect url.
    :param extra_context: Any extra context dict.
    """

    # Compute the post report redirect url
    if post_report_redirect is None:
        post_report_redirect = reverse('contentreport:content_report_done')
    else:
        post_report_redirect = resolve_url(post_report_redirect)

    # Get the content object
    content_obj = get_object_or_404(objects_loader, pk=pk)

    # Handle POST
    if request.method == "POST":
        form = content_report_form(request.POST)
        if form.is_valid():
            opts = {
                'content_obj': content_obj,
                'reporter': request.user,
                'request': request,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_report_redirect)
    else:
        form = content_report_form()

    # Render the template
    context = {
        content_object_name: content_obj,
        'form': form,
        'title': _('Content report'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def report_content_done(request,
                        template_name='contentreport/content_report_done.html',
                        extra_context=None):
    """
    "Thanks" view displayed after reporting a content.
    :param request: The current request.
    :param template_name: The template to be used.
    :param extra_context: Any extra for the template.
    :return: TemplateResponse
    """
    context = {
        'title': _('Content report done'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
