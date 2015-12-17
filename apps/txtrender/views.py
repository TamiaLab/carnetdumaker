"""
Home pages views for the text rendering app.
"""

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from .utils import render_document


@csrf_exempt
def preview_rendering(request,
                      template_name='txtrender/preview.html',
                      extra_context=None):
    """
    Text rendering preview view.
    :param request: The incoming request.
    :param extra_context: Any extra template context information.
    :return: Raw HTML fragment.
    """

    # Check for POST only
    if request.method != 'POST':
        return HttpResponse(_('This view only handle POST requests!'))

    # Check if the user is authenticated
    if not request.user.is_authenticated():
        return HttpResponse(_("Beware! You are not logged-in!"))

    # Get the user input
    user_input = request.POST.get('content', '')

    # Do nothing if no input
    if not user_input:
        return HttpResponse('')

    # Render the user input
    is_staff = request.user.is_staff
    output_html, _, __ = render_document(user_input,
                                         allow_titles=True,
                                         allow_code_blocks=True,
                                         allow_alerts_box=True,
                                         allow_text_formating=True,
                                         allow_text_extra=True,
                                         allow_text_alignments=True,
                                         allow_text_directions=True,
                                         allow_text_modifiers=True,
                                         allow_text_colors=True,
                                         allow_spoilers=True,
                                         allow_figures=True,
                                         allow_lists=True,
                                         allow_todo_lists=True,
                                         allow_definition_lists=True,
                                         allow_tables=True,
                                         allow_quotes=True,
                                         allow_footnotes=True,
                                         allow_acronyms=True,
                                         allow_links=True,
                                         allow_medias=True,
                                         allow_cdm_extra=is_staff,
                                         preview_mode=True,
                                         merge_footnotes_html=True)

    # Return the result
    context = {
        'output_html': output_html,
    }
    return TemplateResponse(request, template_name, context)
