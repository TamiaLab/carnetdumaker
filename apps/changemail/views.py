"""
Views for the change email app.
"""

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from .tokens import default_token_generator
from .forms import EmailChangeForm


# 4 views to change email:
# - change_email
# - change_email_done
# - change_email_confirm
# - change_email_complete

@login_required
@csrf_protect
def change_email(request,
                 template_name='changemail/email_change_form.html',
                 email_template_name='changemail/email_change_email.txt',
                 html_email_template_name=None,
                 subject_template_name='changemail/email_change_subject.txt',
                 email_change_form=EmailChangeForm,
                 token_generator=default_token_generator,
                 post_change_redirect=None,
                 from_email=None,
                 extra_context=None):
    """
    Display the form to change the email address of the current logged-in user.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param email_template_name: The template name to be used for the email body.
    :param html_email_template_name: The template name to be used for the email HTML body.
    :param subject_template_name: The template name to be used for the email subject.
    :param email_change_form: The form class to be used.
    :param token_generator: The token genertor to be used.
    :param post_change_redirect: The post change redirect url.
    :param from_email: The ``from`` email to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Compute the post change redirect url
    if post_change_redirect is None:
        post_change_redirect = reverse('email_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)

    # Handle the form
    if request.method == "POST":
        form = email_change_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = email_change_form()

    # Render the template
    context = {
        'form': form,
        'title': _('Change email address'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def change_email_done(request,
                      template_name='changemail/email_change_done.html',
                      extra_context=None):
    """
    Display the "email change confirmation link sent" view.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Render the template
    context = {
        'title': _('Email change confirmation link sent'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
def change_email_confirm(request, uidb64=None, token=None, addressb64=None,
                         template_name='changemail/email_change_confirm_failed.html',
                         token_generator=default_token_generator,
                         post_confirm_redirect=None,
                         extra_context=None):
    """
    Display the "confirm address change" view.
    :param request: The current request.
    :param uidb64: The user's ID in base64.
    :param addressb64: The new user's email address in base64.
    :param token: The security token.
    :param template_name: The template name to be used.
    :param token_generator: The token generator to be used.
    :param post_confirm_redirect: The post confirm redirect url.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """
    assert uidb64 is not None and token is not None and addressb64 is not None  # checked by URLconf

    # Compute the post confirm redirect url
    if post_confirm_redirect is None:
        post_confirm_redirect = reverse('email_change_complete')
    else:
        post_confirm_redirect = resolve_url(post_confirm_redirect)

    # Decode url parameters
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        address = force_text(urlsafe_base64_decode(addressb64))
        user = get_user_model()._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
        address = None

    # Handle the security token
    if user is not None and \
            address is not None and \
            token_generator.check_token(user, token):

            # Save the new email address
            user.email = address
            user.save(update_fields=('email', ))

            # Redirect to the done view
            return HttpResponseRedirect(post_confirm_redirect)

    # Render the template
    context = {
        'title': _('Email address modification unsuccessful'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def change_email_complete(request,
                          template_name='changemail/email_change_complete.html',
                          extra_context=None):
    """
    Display the "email change complete" view.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Render the template
    context = {
        'title': _('Email change complete'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
