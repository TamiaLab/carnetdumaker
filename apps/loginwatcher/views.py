"""
Views for the log watcher app.
"""

from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

from .models import LogEvent
from .settings import LOG_EVENTS_PER_PAGE


@never_cache
@login_required
def events_history(request,
                   template_name='loginwatcher/events_history.html',
                   extra_context=None):
    """
    Login events history view.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra template context information.
    :return: TemplateResponse
    """

    # Get all last log events
    event_list = LogEvent.objects.filter(username__iexact=request.user.username)[:LOG_EVENTS_PER_PAGE]

    # Render the template
    context = {
        'title': _('Login history'),
        'events': event_list,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
