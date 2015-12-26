"""
Views for the user accounts app.
"""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, resolve_url
from django.core.urlresolvers import reverse_lazy as reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .models import (UserProfile, set_preferred_language_and_timezone)
from .settings import NB_ACCOUNTS_PER_PAGE
from .forms import UserProfileModificationForm


def accounts_list(request,
                  template_name='accounts/accounts_list.html',
                  extra_context=None):
    """
    Accounts page view, display all registered user accounts as a paginated list.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Accounts listing
    user_account_list = UserProfile.objects.get_active_users_accounts().select_related('user')

    # Accounts list pagination
    paginator, page = paginate(user_account_list, request, NB_ACCOUNTS_PER_PAGE)

    # Render the template
    context = {
        'title': _('Members list'),
    }
    update_context_for_pagination(context, 'accounts', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
def public_account_show(request, username,
                        template_name='accounts/public_user_account.html',
                        extra_context=None):
    """
    Public user account page view, display all public information of a specific user.
    :param request: The current request.
    :param username: The user's username.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the requested user instance
    public_user = get_object_or_404(get_user_model().objects.select_related('user_profile'),
                                    username__iexact=username)

    # Get the user status
    http_status = 200 if public_user.is_active else 410

    # Render the template
    context = {
        'public_user': public_user,
        'public_user_profile': public_user.user_profile,
        'title': _('Public profile of %s') % public_user.username,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context, status=http_status)


@never_cache
@csrf_protect
@login_required
def my_account_show(request,
                    template_name='accounts/my_account.html',
                    account_edit_form=UserProfileModificationForm,
                    post_edit_redirect=None,
                    extra_context=None):
    """
    User personal account page view, allow modification of personal information.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param account_edit_form: The account edition form class to be used.
    :param post_edit_redirect: The post edit redirect uri or reverse.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post edit redirect uri
    if post_edit_redirect is None:
        post_edit_redirect = reverse('myaccount:index')
    else:
        post_edit_redirect = resolve_url(post_edit_redirect)

    # Get the current user profile
    current_user = request.user
    current_user_profile = current_user.user_profile

    # Handle the form
    if request.method == "POST":
        form = account_edit_form(request.POST, request.FILES, instance=current_user_profile)
        if form.is_valid():
            form.save()
            set_preferred_language_and_timezone(current_user, request)
            messages.add_message(request, messages.SUCCESS,
                                 _('Your profile information has been successfully updated!'))
            return HttpResponseRedirect(post_edit_redirect)
    else:
        form = account_edit_form(instance=current_user_profile)

    # Render the template
    context = {
        'form': form,
        'title': _('My account'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
