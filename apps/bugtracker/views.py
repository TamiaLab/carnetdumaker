"""
Views for the bug tracker app.
"""

from django.db.models import Prefetch
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, resolve_url
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .models import (IssueTicket,
                     IssueComment,
                     IssueTicketSubscription)
from .forms import (IssueTicketCreationForm,
                    IssueTicketEditionForm,
                    IssueCommentCreationForm,
                    BugTrackerProfileModificationForm)
from .settings import (NB_ISSUES_PER_PAGE,
                       NB_ISSUE_COMMENTS_PER_PAGE,
                       NB_SECONDS_BETWEEN_COMMENTS)


def index(request,
          template_name='bugtracker/bugtracker_index.html',
          extra_context=None):
    """
    Index page of the bug tracker app.
    :param request: The incoming request.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    """
    context = {
        'title': _('Bug tracker index page'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def tickets_list(request,
                 template_name='bugtracker/issueticket_list.html',
                 extra_context=None):
    """
    List of all issue tickets, paginated view.
    Can be sorted using the publication date or modification date with ``?sortby=pubdate`` or ``?sortby=moddate``.
    Can change sort orientation with ``?sortfrom=recent`` (recent to old) or ``?sortfrom=old`` (old to recent).
    Can filter status, priority and difficulty using ``?status=XXX``, ``?priority=XXX`` or/and ``?difficulty=XXX``
    :param request: The incoming request.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    """
    queryset = IssueTicket.objects.all()

    # Prefetch comments and subscribers
    current_user = request.user
    if current_user.is_authenticated():
        prefetch_comments = Prefetch('comments',
                                     queryset=IssueComment.objects.filter(author=current_user),
                                     to_attr='user_comments')
        prefetch_subscriptions = Prefetch('subscribers',
                                          queryset=IssueTicketSubscription.objects.filter(user=current_user),
                                          to_attr='user_subscriptions')
        queryset = queryset.prefetch_related(prefetch_comments, prefetch_subscriptions)

    context = {
        'title': _('Tickets list'),
        }
    if extra_context is not None:
        context.update(extra_context)
    return _generic_tickets_list(queryset, request, template_name, context)


@never_cache
@login_required
def my_tickets_list(request,
                    template_name='bugtracker/issueticket_mylist.html',
                    extra_context=None):
    """
    List of all issue tickets of the current authenticated user, paginated view.
    Can be sorted using the publication date or modification date with ``?sortby=pubdate`` or ``?sortby=moddate``.
    Can change sort orientation with ``?sortfrom=recent`` (recent to old) or ``?sortfrom=old`` (old to recent).
    Can filter status, priority and difficulty using ``?status=XXX``, ``?priority=XXX`` or/and ``?difficulty=XXX``
    :param request: The incoming request.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    """
    queryset = request.user.submitted_issues.all()
    context = {
        'title': _('My tickets list'),
        }
    if extra_context is not None:
        context.update(extra_context)
    return _generic_tickets_list(queryset, request, template_name, context)


def _generic_tickets_list(queryset, request, template_name, context):
    """
    List of all issue tickets from the given queryset, paginated view.
    Can be sorted using the publication date or modification date with ``?sortby=pubdate`` or ``?sortby=moddate``.
    Can change sort orientation with ``?sortfrom=recent`` (recent to old) or ``?sortfrom=old`` (old to recent).
    Can filter status, priority and difficulty using ``?status=XXX``, ``?priority=XXX`` or/and ``?difficulty=XXX``
    :param queryset: The queryset to source data from.
    :param request: The incoming request.
    :param template_name: The template to use for the view.
    :param context: Any extra context dict.
    """

    # Issues sorting
    sort_by = request.GET.get('sortby', 'pubdate')
    sort_from = request.GET.get('sortfrom', 'recent')
    if sort_by == 'moddate':
        if sort_from == 'recent':
            order_by = '-last_modification_date'
        else:
            order_by = 'last_modification_date'
    else:
        if sort_from == 'recent':
            order_by = '-submission_date'
        else:
            order_by = 'submission_date'
    issues_list = queryset.order_by(order_by)

    # Issues filtering
    filter_status = request.GET.get('status', None)
    if filter_status:
        issues_list = issues_list.filter(status=filter_status)
    filter_priority = request.GET.get('priority', None)
    if filter_priority:
        issues_list = issues_list.filter(priority=filter_priority)
    filter_difficulty = request.GET.get('difficulty', None)
    if filter_difficulty:
        issues_list = issues_list.filter(status=filter_difficulty)

    # Issues list pagination
    paginator, page = paginate(issues_list.select_related('submitter'), request, NB_ISSUES_PER_PAGE)

    # Template rendering
    sort_context = {
        'sort_sortby': sort_by,
        'sort_sortfrom': sort_from,
        'sort_status': filter_status,
        'sort_priority': filter_priority,
        'sort_difficulty': filter_difficulty,
    }
    context.update(sort_context)
    update_context_for_pagination(context, 'issues', request, paginator, page)

    return TemplateResponse(request, template_name, context)


@csrf_protect
@login_required
def ticket_create(request,
                  template_name='bugtracker/issueticket_form.html',
                  issue_create_form=IssueTicketCreationForm,
                  extra_context=None):
    """
    Ticket creation view.
    Allow authenticated users to create new ticket.
    :param request: The incoming request.
    :param issue_create_form: The form class to be used for the issue creation.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    """

    # Get the user preferences
    current_user = request.user
    notify_of_reply = current_user.bugtracker_profile.notify_of_reply_by_default

    # Handle POST
    if request.method == "POST":
        form = issue_create_form(request.POST)
        if form.is_valid():
            opts = {
                'request': request,
                'submitter': current_user,
                }
            new_obj = form.save(**opts)

            # Redirect to the newly created ticket
            return HttpResponseRedirect(new_obj.get_absolute_url())
    else:
        form = issue_create_form(initial={'notify_of_reply': notify_of_reply})

    # Render the template
    context = {
        'form': form,
        'title': _('Ticket creation'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@csrf_protect
def ticket_show(request, pk,
                template_name='bugtracker/issueticket_detail.html',
                issue_comment_form=IssueCommentCreationForm,
                extra_context=None):
    """
    Detail view of the given ticket.
    comments can be reverse sorted (from new to old) using the GET parameter ``?sort=reverse``.
    :param pk: The ticket PK.
    :param template_name: The template to use for the view.
    :param issue_comment_form: The issue comment form to be used.
    :param request: The incoming request.
    :param extra_context: Any extra context dict.
    """

    # Reverse comments sorting
    if request.GET.get('sort', None) == 'reverse':
        order_by = '-pub_date'
        cur_order_by = 'reverse'
    else:
        order_by = 'pub_date'
        cur_order_by = ''

    # Get the ticket and related comments
    manager = IssueTicket.objects.select_related('submitter', 'assigned_to', 'component')
    issue_obj = get_object_or_404(manager, pk=pk)
    issue_comments_list = issue_obj.comments.order_by(order_by)

    # Issue's comments pagination
    paginator, page = paginate(issue_comments_list
                               .select_related('author')
                               .prefetch_related('changes'), request, NB_ISSUE_COMMENTS_PER_PAGE)

    # Get the user preferences
    current_user = request.user
    if current_user.is_authenticated():
        notify_of_reply = current_user.bugtracker_profile.notify_of_reply_by_default
        has_subscribe_to_issue = IssueTicketSubscription.objects.has_subscribed_to_issue(current_user, issue_obj)
    else:
        notify_of_reply = False
        has_subscribe_to_issue = False
    is_flooding = False

    # Handle POST requests
    if request.method == "POST":

        # Only authenticated user can post comment
        if not current_user.is_authenticated():
            raise PermissionDenied()

        # Refresh anti flood only on POST
        is_flooding = current_user.bugtracker_profile.is_flooding()

        # Handle form (with anti flood)
        form = issue_comment_form(request.POST)
        if form.is_valid() and not is_flooding:
            opts = {
                'request': request,
                'issue': issue_obj,
                'author': current_user,
                }
            new_obj = form.save(**opts)

            # Re-arm anti flood protection
            current_user.bugtracker_profile.rearm_flooding_delay_and_save()

            # Redirect to the newly created comment
            return HttpResponseRedirect(new_obj.get_absolute_url())
    else:
        form = issue_comment_form(initial={'notify_of_reply': notify_of_reply})

    # Render the template
    context = {
        'cur_order_by': cur_order_by,
        'is_flooding': is_flooding,
        'flood_delay_sec': NB_SECONDS_BETWEEN_COMMENTS,
        'issue': issue_obj,
        'has_subscribe_to_issue': has_subscribe_to_issue,
        'comment_form': form,
        'title': _('Ticket detail'),
        }
    update_context_for_pagination(context, 'issue_comments', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def ticket_edit(request, pk,
                template_name='bugtracker/issueticket_edit.html',
                issue_edit_form=IssueTicketEditionForm,
                extra_context=None):
    """
    Edit view of the given ticket.
    :param request: The incoming request.
    :param pk: The ticket PK.
    :param template_name: The template to use for the view.
    :param issue_edit_form: The issue edition form to be used.
    :param extra_context: Any extra context dict.
    """

    # Get the issue object
    manager = IssueTicket.objects.select_related('submitter', 'assigned_to')
    issue_obj = get_object_or_404(manager, pk=pk)

    # Only the submitter or the staff can edit this issue
    if not issue_obj.can_edit(request.user):
        raise PermissionDenied()

    # Handle POST
    if request.method == "POST":
        form = issue_edit_form(request.POST, instance=issue_obj)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _('Your ticket have been successfully updated!'))
            return HttpResponseRedirect(issue_obj.get_absolute_url())
    else:
        form = issue_edit_form(instance=issue_obj)

    # Render the template
    context = {
        'issue': issue_obj,
        'form': form,
        'title': _('Ticket edition'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def ticket_subscribe(request, pk,
                     template_name='bugtracker/issueticket_subscribe.html',
                     extra_context=None):
    """
    View to subscribe to a ticket.
    :param request: The current request.
    :param pk: The ticket's PK.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the issue object
    issue_obj = get_object_or_404(IssueTicket, pk=pk)

    # Handle POST
    if request.method == "POST":

        # Subscribe
        IssueTicketSubscription.objects.subscribe_to_issue(request.user, issue_obj)

        # Redirect to the issue detail view
        return HttpResponseRedirect(issue_obj.get_absolute_url())

    # Render the template
    context = {
        'issue': issue_obj,
        'title': _('Ticket subscribe'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def ticket_unsubscribe(request, pk,
                       template_name='bugtracker/issueticket_unsubscribe.html',
                       extra_context=None):
    """
    View to unsubscribe from a ticket.
    :param request: The current request.
    :param pk: The ticket's PK.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the issue object
    issue_obj = get_object_or_404(IssueTicket, pk=pk)

    # Handle POST
    if request.method == "POST":

        # Un-subscribe
        IssueTicketSubscription.objects.unsubscribe_from_issue(request.user, issue_obj)

        # Redirect to the issue detail view
        return HttpResponseRedirect(issue_obj.get_absolute_url())

    # Render the template
    context = {
        'issue': issue_obj,
        'title': _('Ticket unsubscribe'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def comment_show(request, pk):
    """
    Permanent redirect to the issue url at the comment anchor.
    :param request: The current request.
    :param pk: The issue's comment PK.
    :return: HttpResponsePermanentRedirect
    """
    assert pk is not None

    # Get the comment or raise 404 (avoid redirect to invalid comment)
    comment_obj = get_object_or_404(IssueComment, pk=pk)

    # Redirect to the real comment detail view
    return HttpResponsePermanentRedirect(comment_obj.get_absolute_url())


@never_cache
@csrf_protect
@login_required
def my_account_show(request,
                    template_name='bugtracker/my_account.html',
                    account_edit_form=BugTrackerProfileModificationForm,
                    post_edit_redirect=None,
                    extra_context=None):
    """
    User bug tracker's account page view, allow modification of bug tracker preferences.
    :param request: The incoming request.
    :param template_name: The template to be used.
    :param account_edit_form: The account edition form class to be used.
    :param post_edit_redirect: The post edit redirect uri or reverse.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post edit redirect uri
    if post_edit_redirect is None:
        post_edit_redirect = reverse('bugtracker:myaccount')
    else:
        post_edit_redirect = resolve_url(post_edit_redirect)

    # Get the current user profile
    current_user_profile = request.user.bugtracker_profile
    assert current_user_profile is not None  # Just in case

    # Handle the form
    if request.method == "POST":
        form = account_edit_form(request.POST, instance=current_user_profile)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 _('Your bug tracker preferences has been successfully updated!'))
            return HttpResponseRedirect(post_edit_redirect)
    else:
        form = account_edit_form(instance=current_user_profile)

    # Render the template
    context = {
        'form': form,
        'title': _('My bug tracker preferences'),
        }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
def my_ticket_subscription_list(request,
                                template_name='bugtracker/issueticket_mysubscriptionslist.html',
                                extra_context=None):
    """
    List of all issue tickets subscribed by the user, paginated view.
    Can be sorted using the publication date or modification date with ``?sortby=pubdate`` or ``?sortby=moddate``.
    Can change sort orientation with ``?sortfrom=recent`` (recent to old) or ``?sortfrom=old`` (old to recent).
    Can filter status, priority and difficulty using ``?status=XXX``, ``?priority=XXX`` or/and ``?difficulty=XXX``
    :param request: The incoming request.
    :param template_name: The template to use for the view.
    :param extra_context: Any extra context dict.
    """
    current_user = request.user
    issue_subscriptions = IssueTicketSubscription.objects.select_related('issue') \
        .filter(user=current_user, active=True)

    # Issues list pagination
    paginator, page = paginate(issue_subscriptions, request, NB_ISSUES_PER_PAGE)

    # Template rendering
    context = {
        'title': _('My tickets subscription list'),
        }
    update_context_for_pagination(context, 'subscriptions', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
