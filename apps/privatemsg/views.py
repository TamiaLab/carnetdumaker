"""
Views for the private messages app.
"""

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, resolve_url
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .models import PrivateMessage, BlockedUser
from .forms import (PrivateMessageCreationForm,
                    PrivateMessageReplyForm,
                    PrivateMessageProfileModificationForm)
from .settings import (NB_PRIVATE_MSG_PER_PAGE,
                       NB_SECONDS_BETWEEN_PRIVATE_MSG,
                       NB_BLOCKED_USERS_PER_PAGE,
                       DELETED_MSG_DELETION_TIMEOUT_DAYS)
from .notifications import notify_of_new_private_message


@never_cache
@login_required
@csrf_protect
def msg_inbox(request, filterby='all',
              template_name='privatemsg/inbox.html',
              extra_context=None):
    """
    Display the inbox for the current user.
    :param request: The current request.
    :param filterby: The selected filtering option.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the messages list for the current user
    messages = PrivateMessage.objects.inbox_for(request.user).select_related('parent_msg', 'sender')

    # Filter the list
    if filterby == 'read':
        messages = messages.filter(read_at__isnull=False)
    elif filterby == 'unread':
        messages = messages.filter(read_at__isnull=True)

    # Messages list pagination
    paginator, page = paginate(messages, request, NB_PRIVATE_MSG_PER_PAGE)

    # Render the template
    context = {
        'title': _('Private messages inbox'),
        'filter_by': filterby
    }
    update_context_for_pagination(context, 'private_messages', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@login_required
@csrf_protect
def mark_all_as_read(request,
                     template_name='privatemsg/mark_all_as_read.html',
                     post_mark_all_read_redirect=None,
                     extra_context=None):
    """
    Mark all unread message of the current user as read.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param post_mark_all_read_redirect: The post action redirect.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post "mark all as read" redirect
    if post_mark_all_read_redirect is None:
        post_mark_all_read_redirect = reverse('privatemsg:inbox')
    else:
        post_mark_all_read_redirect = resolve_url(post_mark_all_read_redirect)

    # Handle "mark all as read" feature
    if request.method == "POST":
        PrivateMessage.objects.mark_all_messages_has_read_for(request.user)
        return HttpResponseRedirect(post_mark_all_read_redirect)

    # Render the template
    context = {
        'title': _('Mark all private messages has read'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
def msg_outbox(request,
               template_name='privatemsg/outbox.html',
               extra_context=None):
    """
    Display the outbox for the current user.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the messages list for the current user
    messages = PrivateMessage.objects.outbox_for(request.user).select_related('parent_msg', 'recipient')

    # Messages list pagination
    paginator, page = paginate(messages, request, NB_PRIVATE_MSG_PER_PAGE)

    # Render the template
    context = {
        'title': _('Private messages outbox'),
    }
    update_context_for_pagination(context, 'private_messages', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
def msg_trashbox(request,
                 template_name='privatemsg/trashbox.html',
                 extra_context=None):
    """
    Display the trashbox for the current user.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the messages list for the current user
    messages = PrivateMessage.objects.trash_for(request.user).select_related('parent_msg', 'sender', 'recipient')

    # Messages list pagination
    paginator, page = paginate(messages, request, NB_PRIVATE_MSG_PER_PAGE)

    # Render the template
    context = {
        'title': _('Private messages trash'),
        'deletion_timeout_days': DELETED_MSG_DELETION_TIMEOUT_DAYS
    }
    update_context_for_pagination(context, 'private_messages', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@login_required
@csrf_protect
def delete_all_deleted_msg_permanently(request,
                                       template_name='privatemsg/trashbox_cleanup.html',
                                       post_delete_redirect=None,
                                       extra_context=None):
    """
    Empty the trashbox for the current user.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param post_delete_redirect: Post delete redirect.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post delete redirect
    if post_delete_redirect is None:
        post_delete_redirect = reverse('privatemsg:trash')
    else:
        post_delete_redirect = resolve_url(post_delete_redirect)

    # Handle "clean trash" feature
    if request.method == "POST":
        PrivateMessage.objects.empty_trash_of(request.user)
        return HttpResponseRedirect(post_delete_redirect)

    # Render the template
    context = {
        'title': _('Clean the trash'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@login_required
@csrf_protect
def msg_compose(request, recipient=None,
                template_name='privatemsg/msg_compose.html',
                msg_compose_form=PrivateMessageCreationForm,
                extra_context=None):
    """
    Compose a new private message.
    :param request: The current request.
    :param recipient: The recipient username (optional)
    :param template_name: The template name to be used.
    :param msg_compose_form: The compose form class.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Useful variables
    current_user = request.user
    is_flooding = False

    # Handle POST requests
    if request.method == "POST":

        # Refresh anti flood only on POST
        is_flooding = current_user.privatemsg_profile.is_flooding()

        # Handle form
        form = msg_compose_form(request.POST, sender=current_user)
        if form.is_valid() and not is_flooding:
            new_obj = form.save()

            # Notify recipient of new message
            notify_of_new_private_message(new_obj, request)

            # Re-arm anti flood protection
            current_user.privatemsg_profile.rearm_flooding_delay_and_save()

            # Redirect to the newly created message
            return HttpResponseRedirect(new_obj.get_absolute_url())
    else:
        form = msg_compose_form(initial={'recipient': recipient or ''}, sender=current_user)

    # Render the template
    context = {
        'is_flooding': is_flooding,
        'flood_delay_sec': NB_SECONDS_BETWEEN_PRIVATE_MSG,
        'form': form,
        'title': _('New private message')
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@login_required
@csrf_protect
def msg_detail(request, pk,
               template_name='privatemsg/msg_detail.html',
               post_mark_unread_redirect=None,
               mark_unread_form_submit_name='mark_unread',
               extra_context=None):
    """
    Display details of a private message.
    :param request: The current request.
    :param pk: The message PK.
    :param template_name: The template name to be used.
    :param post_mark_unread_redirect: The post action redirect.
    :param mark_unread_form_submit_name: The "mark as unread" form action name.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post "mark as read" redirect
    if post_mark_unread_redirect is None:
        post_mark_unread_redirect = reverse('privatemsg:inbox')
    else:
        post_mark_unread_redirect = resolve_url(post_mark_unread_redirect)

    # Get the private message object
    current_user = request.user
    query_base = PrivateMessage.objects.select_related('sender', 'recipient', 'parent_msg')
    message = get_object_or_404(query_base, Q(recipient=current_user) | Q(sender=current_user), pk=pk)

    # Handle POST
    if request.method == "POST":
        if request.POST.get(mark_unread_form_submit_name, None):
            if not message.unread():
                message.read_at = None
                message.save(update_fields=('read_at', ))
            return HttpResponseRedirect(post_mark_unread_redirect)

    # Mark the message as read
    if message.unread() and message.is_recipient(current_user):
        message.read_at = timezone.now()
        message.save(update_fields=('read_at', ))
        msg_just_read = True
    else:
        msg_just_read = False

    # Render the template
    context = {
        'title': _('Private message details'),
        'message': message,
        'msg_just_read': msg_just_read,
        'is_recipient': message.is_recipient(current_user),
        'is_sender': message.is_sender(current_user)
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def msg_reply(request, parent_pk,
              template_name='privatemsg/msg_reply.html',
              msg_reply_form=PrivateMessageReplyForm,
              extra_context=None):
    """
    Reply to a private message.
    :param request: The current request.
    :param parent_pk: Parent message PK.
    :param template_name: The template name to be used.
    :param msg_reply_form: The reply form class.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the parent message object
    current_user = request.user
    query_base = PrivateMessage.objects.select_related('sender', 'recipient', 'parent_msg')
    parent_message = get_object_or_404(query_base, Q(recipient=current_user) | Q(sender=current_user), pk=parent_pk)

    # Useful variables
    is_flooding = False

    # Handle POST requests
    if request.method == "POST":

        # Refresh anti flood only on POST
        is_flooding = current_user.privatemsg_profile.is_flooding()

        # Handle form
        form = msg_reply_form(request.POST, parent_msg=parent_message, sender=current_user)
        if form.is_valid() and not is_flooding:
            new_obj = form.save()

            # Notify recipient of new message
            notify_of_new_private_message(new_obj, request)

            # Re-arm anti flood protection
            current_user.privatemsg_profile.rearm_flooding_delay_and_save()

            # Redirect to the newly created reply
            return HttpResponseRedirect(new_obj.get_absolute_url())
    else:
        form = msg_reply_form(parent_msg=parent_message, sender=current_user)

    # Render the template
    context = {
        'is_flooding': is_flooding,
        'flood_delay_sec': NB_SECONDS_BETWEEN_PRIVATE_MSG,
        'form': form,
        'title': _('Reply to private message'),
        'parent_msg': parent_message
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def my_account_show(request,
                    template_name='privatemsg/my_account.html',
                    account_edit_form=PrivateMessageProfileModificationForm,
                    post_edit_redirect=None,
                    extra_context=None):
    """
    User private message's account page view, allow modification of private message preferences.
    :param request: The incoming request.
    :param template_name: The template to be used.
    :param account_edit_form: The account edition form class to be used.
    :param post_edit_redirect: The post edit redirect uri or reverse.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post edit redirect uri
    if post_edit_redirect is None:
        post_edit_redirect = reverse('privatemsg:myaccount')
    else:
        post_edit_redirect = resolve_url(post_edit_redirect)

    # Get the current user profile
    current_user_profile = request.user.privatemsg_profile
    assert current_user_profile is not None  # Just in case

    # Handle the form
    if request.method == "POST":
        form = account_edit_form(request.POST, instance=current_user_profile)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 _('Your private message preferences has been successfully updated!'))
            return HttpResponseRedirect(post_edit_redirect)
    else:
        form = account_edit_form(instance=current_user_profile)

    # Render the template
    context = {
        'form': form,
        'title': _('My private message preferences'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def msg_delete(request, pk,
               template_name='privatemsg/msg_delete_confirm.html',
               post_delete_redirect=None,
               extra_context=None):
    """
    Move the message to the trash.
    :param request: The current request.
    :param pk: The message PK.
    :param template_name: The template name to be used.
    :param post_delete_redirect: The post delete redirect.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post delete redirect
    if post_delete_redirect is None:
        post_delete_redirect = reverse('privatemsg:trash')
    else:
        post_delete_redirect = resolve_url(post_delete_redirect)

    # Get the message
    current_user = request.user
    message = get_object_or_404(PrivateMessage, Q(recipient=current_user) | Q(sender=current_user), pk=pk)

    # Handle "delete message" feature
    if request.method == "POST":
        message.delete_from_user_side(current_user)
        message.save()
        return HttpResponseRedirect(post_delete_redirect)

    # Render the template
    context = {
        'title': _('Delete message'),
        'message': message
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def msg_delete_permanent(request, pk,
                         template_name='privatemsg/msg_delete_permanent_confirm.html',
                         post_delete_redirect=None,
                         extra_context=None):
    """
    Permanently delete the message.
    :param request: The current request.
    :param pk: The message PK.
    :param template_name: The template name to be used.
    :param post_delete_redirect: The post delete redirect.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post delete redirect
    if post_delete_redirect is None:
        post_delete_redirect = reverse('privatemsg:trash')
    else:
        post_delete_redirect = resolve_url(post_delete_redirect)

    # Get the message
    current_user = request.user
    message = get_object_or_404(PrivateMessage, Q(recipient=current_user) | Q(sender=current_user), pk=pk)

    # Handle "delete message" feature
    if request.method == "POST":
        message.delete_from_user_side(current_user, permanent=True)
        message.save()
        return HttpResponseRedirect(post_delete_redirect)

    # Render the template
    context = {
        'title': _('Permanently delete message'),
        'message': message
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def msg_undelete(request, pk,
                 template_name='privatemsg/msg_undelete_confirm.html',
                 post_undelete_sender_redirect=None,
                 post_undelete_recipient_redirect=None,
                 extra_context=None):
    """
    Udelete a non-permanently deleted message.
    :param request: The current request.
    :param pk: The message PK.
    :param template_name: The template name to be used.
    :param post_undelete_sender_redirect: The post undelete redirect if sender.
    :param post_undelete_recipient_redirect: The post undelete redirect if recipient.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post delete redirects
    if post_undelete_sender_redirect is None:
        post_undelete_sender_redirect = reverse('privatemsg:outbox')
    else:
        post_undelete_sender_redirect = resolve_url(post_undelete_sender_redirect)
    if post_undelete_recipient_redirect is None:
        post_undelete_recipient_redirect = reverse('privatemsg:inbox')
    else:
        post_undelete_recipient_redirect = resolve_url(post_undelete_recipient_redirect)

    # Get the message
    current_user = request.user
    message = get_object_or_404(PrivateMessage, Q(recipient=current_user) | Q(sender=current_user), pk=pk)

    # Handle already permanently deleted message
    if message.permanently_deleted_from_user_side(current_user):
        raise Http404()

    # Choose the right redirect
    if message.is_recipient(current_user):
        post_undelete_redirect = post_undelete_recipient_redirect
    elif message.is_sender(current_user):
        post_undelete_redirect = post_undelete_sender_redirect
    else:
        assert False, "Should never happen"

    # Handle "delete message" feature
    if request.method == "POST":
        message.undelete_from_user_side(current_user)
        message.save()
        return HttpResponseRedirect(post_undelete_redirect)

    # Render the template
    context = {
        'title': _('Un-delete message'),
        'message': message
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def blocked_user_list(request,
                      template_name='privatemsg/blocked_user_list.html',
                      extra_context=None):
    """
    Display all blocked user for the current user.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get all blocked user list for the current user
    blocked_user_list = BlockedUser.objects.blocked_users_for(request.user).select_related('blocked_user')

    # User list pagination
    paginator, page = paginate(blocked_user_list, request, NB_BLOCKED_USERS_PER_PAGE)

    # Render the template
    context = {
        'title': _('Blocked users list'),
    }
    update_context_for_pagination(context, 'blocked_users', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def block_user(request, username,
               post_block_redirect=None,
               template_name='privatemsg/block_user.html',
               extra_context=None):
    """
    View to block an user from sending private message to us.
    :param request: The current request.
    :param username: The user's username to be blocked.
    :param post_block_redirect: The post block redirect uri.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post block redirect
    if post_block_redirect is None:
        post_block_redirect = reverse('privatemsg:blocked_users')
    else:
        post_block_redirect = resolve_url(post_block_redirect)

    # Get the user object
    blocked_user_obj = get_object_or_404(get_user_model(), username=username)

    # Cannot block yourself
    user_is_stupid = request.user == blocked_user_obj

    # Handle POST
    if request.method == "POST" and not user_is_stupid:

        # Subscribe
        BlockedUser.objects.block_user(request.user, blocked_user_obj)

        # Redirect to the blocked user list view
        return HttpResponseRedirect(post_block_redirect)

    # Render the template
    context = {
        'blocked_user': blocked_user_obj,
        'title': _('Block user'),
        'trying_self_block': user_is_stupid
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def unblock_user(request, username,
                 post_unblock_redirect=None,
                 template_name='privatemsg/unblock_user.html',
                 extra_context=None):
    """
    View to unblock an user from sending private message to us.
    :param request: The current request.
    :param username: The user's username to be unblocked.
    :param post_unblock_redirect: The post unblock redirect uri.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post block redirect
    if post_unblock_redirect is None:
        post_unblock_redirect = reverse('privatemsg:blocked_users')
    else:
        post_unblock_redirect = resolve_url(post_unblock_redirect)

    # Get the user object
    blocked_user_obj = get_object_or_404(get_user_model(), username=username)

    # Handle POST
    if request.method == "POST":

        # Subscribe
        BlockedUser.objects.unblock_user(request.user, blocked_user_obj)

        # Redirect to the blocked user list view
        return HttpResponseRedirect(post_unblock_redirect)

    # Render the template
    context = {
        'blocked_user': blocked_user_obj,
        'title': _('Unblock user'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
