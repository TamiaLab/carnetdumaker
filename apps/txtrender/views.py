"""
Home pages views for the text rendering app.
"""

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import render_html


@csrf_exempt
def preview_rendering(request,
                      extra_context=None):
    """
    Text rendering preview view.
    :param request: The incoming request.
    :param extra_context: Any extra template context information.
    :return: Raw HTML fragment.
    """

    # Check for POST only
    if request.method != 'POST':
        return HttpResponse('This view only handle POST requests.')

    # Check if the user is authenticated
    if not request.user.is_authenticated():
        return HttpResponse("<strong>ATTENTION: Vous n'êtes pas connecté !</strong>")

    # Get the user input
    user_input = request.POST.get('content', '')

    # Do nothing if no input
    if not user_input:
        return HttpResponse('')

    # Render the user input
    output_html = render_html(user_input)

    # Return the result
    return HttpResponse(output_html)
