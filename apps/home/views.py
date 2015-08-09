"""
Home pages views for the home pages app.
"""

from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse


def home_page(request,
              template_name='home/home.html',
              extra_context=None):
    """
    Home page view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """
    context = {
        'title': _('Home page'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
