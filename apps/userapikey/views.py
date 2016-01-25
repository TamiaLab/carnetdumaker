"""
Views for the user API keys app.
"""

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from .models import UserApiKey
from .forms import KeyRegenerationConfirmationForm


@never_cache
@login_required
def show_mykey(request,
               template_name='userapikey/show_mykey.html',
               extra_context=None):
    """
    Display the API key of the current logged-in user.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Fetch the current user API key
    api_key = UserApiKey.objects.get_user_key(request.user)

    # Render the template
    context = {
        'api_key': api_key,
        'title': _('My API key'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@login_required
@csrf_protect
def regen_mykey(request,
                template_name='userapikey/regen_mykey_form.html',
                regenerate_key_form=KeyRegenerationConfirmationForm,
                post_regeneration_redirect=None,
                extra_context=None):
    """
    Display the form to regenerate the API key of the current logged-in user.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param regenerate_key_form: The confirmation form to be used.
    :param post_regeneration_redirect: The post key regeneration redirect url.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Compute the post key regeneration redirect url
    if post_regeneration_redirect is None:
        post_regeneration_redirect = reverse('userapikey:index')
    else:
        post_regeneration_redirect = resolve_url(post_regeneration_redirect)

    # Handle the form
    if request.method == "POST":
        form = regenerate_key_form(request.POST)
        if form.is_valid():
            UserApiKey.objects.regenerate_user_key(request.user)
            return HttpResponseRedirect(post_regeneration_redirect)
    else:
        form = regenerate_key_form()

    # Render the template
    context = {
        'form': form,
        'title': _('Regenerate my API key'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
