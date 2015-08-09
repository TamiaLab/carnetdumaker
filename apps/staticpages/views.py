"""
Views for the static pages app.
"""

from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse


def index_page(request,
               template_name='staticpages/index.html',
               extra_context=None):
    """
    "Index page" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Static pages'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def why_this_site(request,
                  template_name='staticpages/why_this_site.html',
                  extra_context=None):
    """
    "Why this site" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Why this site?'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def about_us(request,
             template_name='staticpages/about_us.html',
             extra_context=None):
    """
    "About us" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('About us'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def contact_us(request,
               template_name='staticpages/contact_us.html',
               extra_context=None):
    """
    "contact us" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Contact us'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def cookies_usage(request,
                  template_name='staticpages/cookies_usage.html',
                  extra_context=None):
    """
    "Cookies usage" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Cookies usage'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def legal_notices(request,
                  template_name='staticpages/legal_notices.html',
                  extra_context=None):
    """
    "Legal notices" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Legal notices'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def faq(request,
        template_name='staticpages/faq.html',
        extra_context=None):
    """
    "FAQ" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Faq'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def our_commitments(request,
                    template_name='staticpages/our_commitments.html',
                    extra_context=None):
    """
    "Our commitments" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Our commitments'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def human_sitemap(request,
                  template_name='staticpages/human_sitemap.html',
                  extra_context=None):
    """
    "Sitemap" static page view (human sitemap, no XML here).
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Sitemap'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def tos(request,
        template_name='staticpages/tos.html',
        extra_context=None):
    """
    "Terms of service" static page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Terms of service'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
