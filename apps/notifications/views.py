"""
Views for the notifications app.
"""

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, resolve_url
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .models import Notification
from .forms import NotificationsProfileModificationForm
from .settings import (NB_NOTIFICATIONS_PER_PAGE,
                       READ_NOTIFICATION_DELETION_TIMEOUT_DAYS)


@never_cache
@login_required
def notification_list(request, filterby='all',
                      template_name='notifications/notification_list.html',
                      extra_context=None):
    """
    Notifications list view, can display all notifications, unread ones or only read ones using ``filterby``
    parameter (valid options: None, 'read' or 'unread').
    :param request: The current request.
    :param filterby: The filtering option (None, read or unread)
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the notifications list for the current user
    notifications = Notification.objects.filter(recipient=request.user)

    # Filter the list
    if filterby == 'read':
        notifications = notifications.filter(unread=False)
    elif filterby == 'unread':
        notifications = notifications.filter(unread=True)

    # Notifications list pagination
    paginator, page = paginate(notifications, request, NB_NOTIFICATIONS_PER_PAGE)

    # Render the template
    context = {
        'title': _('Notifications list'),
        'filter_by': filterby,
        'deletion_timeout_days': READ_NOTIFICATION_DELETION_TIMEOUT_DAYS
    }
    update_context_for_pagination(context, 'notifications', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def mark_all_as_read(request,
                     template_name='notifications/mark_all_as_read.html',
                     post_mark_all_read_redirect=None,
                     extra_context=None):
    """
    Mark all unread notifications as read.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param post_mark_all_read_redirect: The post mark all as read redirect.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post "mark all as read" redirect
    if post_mark_all_read_redirect is None:
        post_mark_all_read_redirect = reverse('notifications:index')
    else:
        post_mark_all_read_redirect = resolve_url(post_mark_all_read_redirect)

    # Handle "mark all as read" feature
    if request.method == "POST":
        Notification.objects.mark_all_notifications_has_read(request.user)
        return HttpResponseRedirect(post_mark_all_read_redirect)

    # Render the template
    context = {
        'title': _('Mark all notifications as read'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@login_required
@csrf_protect
def notification_detail(request, pk,
                        template_name='notifications/notification_detail.html',
                        post_mark_unread_redirect=None,
                        mark_unread_form_submit_name='mark_unread',
                        extra_context=None):
    """
    Notifications detail view.
    Also support a POST submit parameter to mark the notification as unread.
    :param request: The current request.
    :param pk: The notification's PK.
    :param post_mark_unread_redirect: The post "mark as unread" redirect reverse.
    :param mark_unread_form_submit_name: POST submit parameter for the "mark as unread" feature.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post "mark as read" redirect
    if post_mark_unread_redirect is None:
        post_mark_unread_redirect = reverse('notifications:index')
    else:
        post_mark_unread_redirect = resolve_url(post_mark_unread_redirect)

    # Get the notification object
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)

    # Handle POST
    if request.method == "POST":
        if request.POST.get(mark_unread_form_submit_name, None):
            if not notification.unread:
                notification.unread = True
                notification.save()
            return HttpResponseRedirect(post_mark_unread_redirect)

    # Mark the notification as read
    if notification.unread:
        notification.unread = False
        notification.save()

    context = {
        'title': _('Notification details'),
        'notification': notification
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def my_account_show(request,
                    template_name='notifications/my_account.html',
                    account_edit_form=NotificationsProfileModificationForm,
                    post_edit_redirect=None,
                    extra_context=None):
    """
    User notification's account page view, allow modification of notification preferences.
    :param request: The incoming request.
    :param template_name: The template to be used.
    :param account_edit_form: The account edition form class to be used.
    :param post_edit_redirect: The post edit redirect uri or reverse.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post edit redirect uri
    if post_edit_redirect is None:
        post_edit_redirect = reverse('notifications:myaccount')
    else:
        post_edit_redirect = resolve_url(post_edit_redirect)

    # Get the current user profile
    current_user_profile = request.user.notifications_profile
    assert current_user_profile is not None  # Just in case

    # Handle the form
    if request.method == "POST":
        form = account_edit_form(request.POST, instance=current_user_profile)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 _('Your notification preferences has been successfully updated!'))
            return HttpResponseRedirect(post_edit_redirect)
    else:
        form = account_edit_form(instance=current_user_profile)

    # Render the template
    context = {
        'form': form,
        'title': _('My notification preferences'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
