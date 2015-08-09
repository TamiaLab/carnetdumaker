"""
Views for the registration app.
"""

from django.db import IntegrityError
from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from apps.registration.forms import UserRegistrationForm

from .models import UserRegistrationProfile
from .settings import REGISTRATION_OPEN


# 5 views for user registration:
# - register_user create a new inactive user and sends the mail with the activation link
# - register_user_done shows a success message for the above
# - register_user_closed shows an error message saying new user registration is not allowed
# - activate_user checks the activation link and activate the user account if valid
# - activate_user_complete shows a success message for the above

@sensitive_post_parameters()
@csrf_protect
def register_user(request,
                  template_name='registration/registration_form.html',
                  email_template_name='registration/activate_user_email.txt',
                  html_email_template_name=None,
                  subject_template_name='registration/activate_user_email_subject.txt',
                  registration_form=UserRegistrationForm,
                  post_register_redirect=None,
                  registration_closed_redirect=None,
                  from_email=None,
                  extra_context=None):
    """
    Create a new inactive user and sends the mail with the activation link in it.
    :param request: The incoming request.
    :param template_name: The template name to be used for the form.
    :param email_template_name: The template name to be used for the email text body.
    :param html_email_template_name: The template name to be used for the email HTML body.
    :param subject_template_name: The template name to be used for the email subject.
    :param registration_form: The form class to be used.
    :param post_register_redirect: The post registration redirect uri or reverse.
    :param registration_closed_redirect: The closed registration redirect uri or reverse.
    :param from_email: The "from" email address. Use ``None`` to use the default settings.
    :param extra_context: Any extra context for the form template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Redirect to the closed registration page if necessary
    if not REGISTRATION_OPEN:
        if registration_closed_redirect is None:
            registration_closed_redirect = reverse('registration_closed')
        else:
            registration_closed_redirect = resolve_url(registration_closed_redirect)
        return HttpResponseRedirect(registration_closed_redirect)

    # Compute the post register redirect
    if post_register_redirect is None:
        post_register_redirect = reverse('registration_done')
    else:
        post_register_redirect = resolve_url(post_register_redirect)

    # Handle POST
    save_failed = False
    if request.method == "POST":
        form = registration_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'from_email': from_email,
                'email_template_name': email_template_name,
                'html_email_template_name': html_email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                }
            try:
                form.save(**opts)
            except IntegrityError:
                save_failed = True
            else:
                return HttpResponseRedirect(post_register_redirect)
    else:
        form = registration_form()

    # Render the template
    context = {
        'form': form,
        'save_failed': save_failed,
        'title': _('User registration'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def register_user_done(request,
                       template_name='registration/register_user_done.html',
                       extra_context=None):
    """
    Simple template view displayed after the registration form is submitted.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """
    context = {
        'title': _('Registration done'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def register_user_closed(request,
                         template_name='registration/register_user_closed.html',
                         extra_context=None):
    """
    Simple template view displayed registration are closed.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """
    context = {
        'title': _('Registration closed'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
def activate_user(request, uidb64=None, activation_key=None,
                  template_name='registration/activate_user_failed.html',
                  post_activate_redirect=None,
                  extra_context=None):
    """
    View to check the activation link and activate the related user if all right.
    :param request: The incoming request.
    :param uidb64: The user account PK encoded in base 64.
    :param activation_key: The activation key.
    :param template_name: The template name to be used.
    :param post_activate_redirect: The post activation redirect uri or reverse.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert uidb64 is not None and activation_key is not None  # checked by URLconf

    # Compute the post activate redirect
    if post_activate_redirect is None:
        post_activate_redirect = reverse('registration_complete')
    else:
        post_activate_redirect = resolve_url(post_activate_redirect)

    # Get the user
    try:
        uid = urlsafe_base64_decode(uidb64)
        user_registration_profile = UserRegistrationProfile.objects.get(user__pk=uid)
    except (TypeError, ValueError, OverflowError, UserRegistrationProfile.DoesNotExist):
        user_registration_profile = None

    # Activate the user and redirect if ok
    if user_registration_profile is not None and user_registration_profile.activation_key_valid(activation_key):
        user_registration_profile.activate_user()
        return HttpResponseRedirect(post_activate_redirect)

    # Render the (error) template
    context = {
        'title': _('Account activation unsuccessful'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def activate_user_complete(request,
                           template_name='registration/activate_user_complete.html',
                           extra_context=None):
    """
    Simple template view displayed after user's account activation is complete.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """
    context = {
        'title': _('Registration complete'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
