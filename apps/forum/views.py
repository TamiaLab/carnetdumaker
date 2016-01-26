"""
Views for the forum app.
"""

from collections import defaultdict

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, resolve_url
from django.utils.translation import ugettext_lazy as _
from django.http import (HttpResponseRedirect,
                         HttpResponsePermanentRedirect)
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.contrib import messages

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)
from apps.txtrender.utils import render_quote

from .settings import (NB_FORUM_THREAD_PER_PAGE,
                       NB_FORUM_POST_PER_PAGE,
                       NB_FORUM_POST_ON_REPLY_PAGE,
                       NB_SECONDS_BETWEEN_POSTS)
from .models import (Forum,
                     ForumSubscription,
                     ForumThread,
                     ForumThreadSubscription,
                     ForumThreadPost,
                     ReadForumTracker,
                     ReadForumThreadTracker)
from .forms import (ForumThreadCreationForm,
                    ForumThreadEditionForm,
                    ForumThreadDeleteForm,
                    ForumThreadReplyForm,
                    ForumThreadPostEditForm,
                    ForumThreadPostDeleteForm,
                    ForumProfileModificationForm)


def forum_index(request,
                template_name='forum/forum_index.html',
                extra_context=None):
    """
    Forum's index page. List all root forums.
    :param request: The current request.
    :param template_name: The template to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all root forums
    root_forums = Forum.objects.root_forums().select_related('category').prefetch_related('children')

    # Group by category
    root_forums_by_cat = defaultdict(list)
    for forum in root_forums:
        root_forums_by_cat[forum.category].append(forum)
    root_forums_by_cat = sorted(root_forums_by_cat.items(), key=lambda x: x[0].ordering if x[0] else -1)

    # Render the template
    context = {
        'title': _('Forum home page'),
        'root_forums': root_forums,
        'root_forums_by_cat': root_forums_by_cat,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def forum_show(request, hierarchy,
               template_name='forum/forum_detail.html',
               extra_context=None):
    """
    Detail view for the specified forum or sub-forum.
    :param hierarchy: The desired forum's slug hierarchy.
    :param request: The current request.
    :param template_name: The template to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """
    assert hierarchy is not None

    # Get the forum object
    forum_obj = get_object_or_404(Forum, slug_hierarchy=hierarchy)

    # Check authorization if forum is private
    if not forum_obj.has_access(request.user):
        raise PermissionDenied()

    # Get all threads in this forum
    queryset = ForumThread.objects.display_ordered(forum_obj) \
        .select_related('first_post__author', 'last_post__author')

    # Prefetch posts and subscriptions
    current_user = request.user
    if current_user.is_authenticated():
        prefetch_posts = Prefetch('posts',
                                  queryset=ForumThreadPost.objects.filter(author=current_user),
                                  to_attr='user_posts')
        prefetch_subscriptions = Prefetch('subscribers',
                                          queryset=ForumThreadSubscription.objects.filter(user=current_user),
                                          to_attr='user_subscriptions')
        queryset = queryset.prefetch_related(prefetch_posts, prefetch_subscriptions)

    # Related thread list pagination
    paginator, page = paginate(queryset, request, NB_FORUM_THREAD_PER_PAGE)

    # Prefetch child forums
    if not page.has_previous():
        child_forums = forum_obj.children.all().order_by('ordering')
    else:
        # Avoid useless SQL request on other pages
        child_forums = None

    # Avoid useless SQL request for anonymous
    if current_user.is_authenticated():
        has_subscribe_to_forum = ForumSubscription.objects.has_subscribed_to_forum(current_user, forum_obj)
    else:
        has_subscribe_to_forum = False

    # Render the template
    context = {
        'title': _('Forum %s') % forum_obj.title,
        'forum': forum_obj,
        'child_forums': child_forums,
        'has_subscribe_to_forum': has_subscribe_to_forum
    }
    update_context_for_pagination(context, 'threads', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    # Prefetch read markers
    if current_user.is_authenticated():
        parent_forum_last_read_date = ReadForumTracker.objects.get_marker_for_forum(current_user, forum_obj)
        thread_markers = ReadForumThreadTracker.objects.get_marker_for_threads(current_user, page.object_list)
        context['read_markers'] = {
            'parent_forum_last_read_date': parent_forum_last_read_date,
            'thread_markers': thread_markers
        }

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
@csrf_protect
def forum_mark_all_thread_as_read(request, hierarchy,
                                  template_name='forum/mark_all_threads_as_read.html',
                                  extra_context=None):
    """
    Mark all unread thread as read.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the forum object
    forum_obj = get_object_or_404(Forum, slug_hierarchy=hierarchy)

    # Check authorization if forum is private
    if not forum_obj.has_access(request.user):
        raise PermissionDenied()

    # Handle "mark all as read" feature
    if request.method == "POST":
        ReadForumTracker.objects.mark_forum_as_read(request.user, forum_obj)
        return HttpResponseRedirect(forum_obj.get_absolute_url())

    # Render the template
    context = {
        'title': _('Mark all threads as read'),
        'forum': forum_obj,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_subscribe(request, hierarchy,
                    template_name='forum/forum_subscribe.html',
                    extra_context=None):
    """
    View for subscribing to the given forum.
    :param request: The current request.
    :param hierarchy: The forum's slug hierarchy.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the forum object
    forum_obj = get_object_or_404(Forum, slug_hierarchy=hierarchy)

    # Handle POST
    if request.method == "POST":

        # Subscribe
        ForumSubscription.objects.subscribe_to_forum(request.user, forum_obj)

        # Redirect to the forum detail view
        return HttpResponseRedirect(forum_obj.get_absolute_url())

    # Render the template
    context = {
        'forum': forum_obj,
        'title': _('Forum subscribe'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_unsubscribe(request, hierarchy,
                      template_name='forum/forum_unsubscribe.html',
                      extra_context=None):
    """
    View for unsubscribing from the given forum.
    :param request: The current request.
    :param hierarchy: The forum's slug hierarchy.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the forum object
    forum_obj = get_object_or_404(Forum, slug_hierarchy=hierarchy)

    # Handle POST
    if request.method == "POST":

        # Unsubscribe
        ForumSubscription.objects.unsubscribe_from_forum(request.user, forum_obj)

        # Redirect to the forum detail view
        return HttpResponseRedirect(forum_obj.get_absolute_url())

    # Render the template
    context = {
        'forum': forum_obj,
        'title': _('Forum unsubscribe'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_thread_create(request, hierarchy,
                        template_name='forum/forum_thread_create.html',
                        template_name_closed_forum='forum/forum_closed.html',
                        forum_thread_create_form=ForumThreadCreationForm,
                        extra_context=None):
    """
    Create forum's thread view.
    :param hierarchy: Parent forum slug hierarchy.
    :param request: The current request.
    :param template_name: The template to be used.
    :param template_name_closed_forum: The template to be used if the forum is closed.
    :param forum_thread_create_form: Form class to use.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert hierarchy is not None

    # Retrieve the parent forum object
    forum_obj = get_object_or_404(Forum, slug_hierarchy=hierarchy)

    # Handle private forum
    if not forum_obj.has_access(request.user):
        raise PermissionDenied()

    # Handle closed forum
    if forum_obj.closed:

        # Render "closed forum" template
        context = {
            'forum': forum_obj,
            'title': _('Forum closed'),
        }
        if extra_context is not None:
            context.update(extra_context)

        return TemplateResponse(request, template_name_closed_forum, context)

    # Handle anti flood
    current_user = request.user
    is_flooding = False

    # Get default notify settings
    notify_of_reply_default = current_user.forum_profile.notify_of_reply_by_default

    # Handle form GET/POST
    if request.method == "POST":

        # Really check for flood on POST only
        is_flooding = current_user.forum_profile.is_flooding()

        # Handle the form
        form = forum_thread_create_form(request.POST, request.FILES)
        if form.is_valid() and not is_flooding:
            opts = {
                'parent_forum': forum_obj,
                'author': current_user,
                'request': request,
            }
            new_thread = form.save(**opts)

            # Re-arm the anti flood timer
            current_user.forum_profile.rearm_flooding_delay_and_save()

            # Redirect to the thread view
            return HttpResponseRedirect(new_thread.get_absolute_url())
    else:
        form = forum_thread_create_form(initial={'notify_of_reply': notify_of_reply_default})

    # Render the template
    context = {
        'forum': forum_obj,
        'form': form,
        'title': _('Create a new topic'),
        'is_flooding': is_flooding,
        'flood_delay_sec': NB_SECONDS_BETWEEN_POSTS
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@csrf_protect
def forum_thread_show(request, pk, slug,
                      template_name='forum/forum_thread_detail.html',
                      mark_as_unread_post_action='mark_unread',
                      extra_context=None):
    """
    Detail view of the given forum's thread.
    :param request: The current request.
    :param pk: The forum's thread's PK.
    :param slug: The forum's thread's slug.
    :param template_name: The template name to be used.
    :param mark_as_unread_post_action: "mark as unread" POST submit name.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """
    assert slug is not None

    # Get the thread object by pk
    manager = ForumThread.objects.published().select_related('parent_forum', 'first_post__author')
    thread_obj = get_object_or_404(manager, pk=pk, slug=slug)

    # Handle private thread
    if not thread_obj.has_access(request.user):
        raise PermissionDenied()

    # Handle "mark as unread" action
    current_user = request.user
    if request.method == 'POST' and current_user.is_authenticated():
        if request.POST.get(mark_as_unread_post_action, None):

            # Mark as unread
            ReadForumThreadTracker.objects.mark_thread_as_unread(current_user, thread_obj)

            # Redirect to the parent forum
            return HttpResponseRedirect(thread_obj.parent_forum.get_absolute_url())

    # Paginate thread's posts
    paginator, page = paginate(thread_obj.posts.published().order_by('pub_date')
                               .select_related('author__user_profile', 'last_modification_by')
                               .prefetch_related('attachments'), request, NB_FORUM_POST_PER_PAGE)

    # Check if the current user has subscribed to the thread
    if current_user.is_authenticated():
        has_subscribe_to_thread = ForumThreadSubscription.objects.has_subscribed_to_thread(current_user, thread_obj)

        # Also handle read marker
        ReadForumThreadTracker.objects.mark_thread_as_read(current_user, thread_obj)
    else:
        has_subscribe_to_thread = False

    # Render the template
    context = {
        'title': _('Thread %s') % thread_obj.title,
        'thread': thread_obj,
        'forum': thread_obj.parent_forum,
        'has_subscribe_to_thread': has_subscribe_to_thread,
    }
    update_context_for_pagination(context, 'posts', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def topic_subscribe(request, pk, slug,
                    template_name='forum/forum_thread_subscribe.html',
                    extra_context=None):
    """
    View for subscribing to the given forum's thread.
    :param request: The current request.
    :param pk: The forum's thread's PK.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the forum's thread object
    manager = ForumThread.objects.published().select_related('parent_forum', 'first_post__author')
    thread_obj = get_object_or_404(manager, pk=pk, slug=slug)

    # Handle edit permission
    current_user = request.user
    if not thread_obj.has_access(current_user):
        raise PermissionDenied()

    # Handle POST
    if request.method == "POST":

        # Subscribe
        ForumThreadSubscription.objects.subscribe_to_thread(request.user, thread_obj)

        # Redirect to the forum's thread detail view
        return HttpResponseRedirect(thread_obj.get_absolute_url())

    # Render the template
    context = {
        'thread': thread_obj,
        'forum': thread_obj.parent_forum,
        'title': _('Forum thread subscribe'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def topic_unsubscribe(request, pk, slug,
                      template_name='forum/forum_thread_unsubscribe.html',
                      extra_context=None):
    """
    View for unsubscribing from the given forum's thread.
    :param request: The current request.
    :param pk: The forum's thread's PK.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Get the forum's thread object
    manager = ForumThread.objects.published().select_related('parent_forum', 'first_post__author')
    thread_obj = get_object_or_404(manager, pk=pk, slug=slug)

    # Handle edit permission
    current_user = request.user
    if not thread_obj.has_access(current_user):
        raise PermissionDenied()

    # Handle POST
    if request.method == "POST":

        # Unsubscribe
        ForumThreadSubscription.objects.unsubscribe_from_thread(request.user, thread_obj)

        # Redirect to the forum's thread detail view
        return HttpResponseRedirect(thread_obj.get_absolute_url())

    # Render the template
    context = {
        'thread': thread_obj,
        'forum': thread_obj.parent_forum,
        'title': _('Forum thread unsubscribe'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_thread_edit(request, pk, slug,
                      template_name='forum/forum_thread_edit.html',
                      forum_thread_edition_form=ForumThreadEditionForm,
                      extra_context=None):
    """
    Edit view for the given forum's thread.
    :param request: The current request.
    :param pk: The forum's thread's PK.
    :param template_name: The template name to be used.
    :param forum_thread_edition_form: The form class to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert pk is not None

    # Get the thread object by pk
    manager = ForumThread.objects.published().select_related('parent_forum', 'first_post__author')
    thread_obj = get_object_or_404(manager, pk=pk, slug=slug)

    # Handle edit permission
    current_user = request.user
    if not thread_obj.can_edit(current_user):
        raise PermissionDenied()

    # Handle form GET/POST
    if request.method == "POST":
        form = forum_thread_edition_form(request.POST, request.FILES, instance=thread_obj)
        if form.is_valid():
            opts = {
                'author': request.user,
                'request': request,
            }
            form.save(**opts)
            return HttpResponseRedirect(thread_obj.get_absolute_url())
    else:
        form = forum_thread_edition_form(instance=thread_obj)

    # Render the template
    context = {
        'thread': thread_obj,
        'forum': thread_obj.parent_forum,
        'form': form,
        'title': _('Edit thread'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_thread_delete(request, pk, slug,
                        template_name='forum/forum_thread_delete.html',
                        forum_thread_deletion_form=ForumThreadDeleteForm,
                        extra_context=None):
    """
    Forum thread delete view.
    :param request: The current request.
    :param pk: The forum's thread PK.
    :param template_name: The template name to be used.
    :param forum_thread_deletion_form: The forum class to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert pk is not None

    # Get the thread object by pk
    manager = ForumThread.objects.published().select_related('parent_forum', 'first_post__author')
    thread_obj = get_object_or_404(manager, pk=pk, slug=slug)

    # Compute the post edit redirection
    post_delete_redirect = thread_obj.parent_forum.get_absolute_url()

    # Handle delete permission
    current_user = request.user
    if not thread_obj.can_delete(current_user):
        raise PermissionDenied()

    # Handle form GET/POST
    if request.method == "POST":
        form = forum_thread_deletion_form(request.POST)
        if form.is_valid():
            opts = {
                'thread': thread_obj,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_delete_redirect)
    else:
        form = forum_thread_deletion_form()

    # Render the template
    context = {
        'thread': thread_obj,
        'forum': thread_obj.parent_forum,
        'form': form,
        'title': _('Delete thread'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_thread_reply(request, pk, slug,
                       template_name='forum/forum_thread_reply.html',
                       template_name_closed_thread='forum/forum_thread_closed.html',
                       forum_thread_reply_form=ForumThreadReplyForm,
                       extra_context=None):
    """
    Forum's thread reply view.
    :param request: The current request.
    :param pk: The forum's thread's PK.
    :param template_name: The template name to be used.
    :param template_name_closed_thread: The template name to be used if the thread is closed.
    :param forum_thread_reply_form: The form class to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert pk is not None

    # Get the thread object by pk
    manager = ForumThread.objects.published().select_related('parent_forum', 'first_post__author')
    thread_obj = get_object_or_404(manager, pk=pk, slug=slug)

    # Handle private forum
    if not thread_obj.has_access(request.user):
        raise PermissionDenied()

    # Handle closed thread
    if thread_obj.closed or thread_obj.locked:

        # Render the "closed thread" template
        context = {
            'thread': thread_obj,
            'forum': thread_obj.parent_forum,
            'title': _('Thread closed'),
        }
        if extra_context is not None:
            context.update(extra_context)

        return TemplateResponse(request, template_name_closed_thread, context)

    # Handle anti flood
    current_user = request.user
    is_flooding = False

    # Get default notify settings
    notify_of_reply_default = current_user.forum_profile.notify_of_reply_by_default

    # Handle form GET/POST
    if request.method == "POST":

        # Check for flood on POST only
        is_flooding = current_user.forum_profile.is_flooding()

        # Handle form and anti flood
        form = forum_thread_reply_form(request.POST, request.FILES)
        if form.is_valid() and not is_flooding:
            opts = {
                'author': current_user,
                'parent_thread': thread_obj,
                'request': request
            }
            new_post = form.save(**opts)
            return HttpResponseRedirect(new_post.get_absolute_url())
    else:
        form = forum_thread_reply_form(initial={'notify_of_reply': notify_of_reply_default})

    # Render the template
    context = {
        'thread': thread_obj,
        'forum': thread_obj.parent_forum,
        'latest_posts': thread_obj.posts.published().order_by('-id')[:NB_FORUM_POST_ON_REPLY_PAGE],
        'form': form,
        'title': _('Reply to thread'),
        'is_flooding': is_flooding,
        'flood_delay_sec': NB_SECONDS_BETWEEN_POSTS
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def forum_thread_post_show(request, pk):
    """
    Permanent redirect to the thread url at the post anchor.
    :param request: The current request.
    :param pk: The thread's post PK.
    :return: HttpResponsePermanentRedirect
    """
    assert pk is not None

    # Get the post or raise 404 (avoid redirect to invalid post)
    thread_post = get_object_or_404(ForumThreadPost.objects.published(), pk=pk)

    # Redirect to the real post detail view
    return HttpResponsePermanentRedirect(thread_post.get_absolute_url())


@never_cache
@csrf_protect
@login_required
def forum_thread_post_reply(request, pk,
                            template_name='forum/forum_thread_post_reply.html',
                            template_name_closed_thread='forum/forum_thread_closed.html',
                            forum_thread_reply_form=ForumThreadReplyForm,
                            extra_context=None):
    """
    Post reply view.
    :param request: The current request.
    :param pk: The quoted post PK.
    :param template_name: The template name to be used.
    :param template_name_closed_thread: The template name to be used if the thread is closed.
    :param forum_thread_reply_form: The form class to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert pk is not None

    # Get the post object by PK
    manager = ForumThreadPost.objects.published().select_related('parent_thread',
                                                                 'parent_thread__parent_forum',
                                                                 'author')
    post_obj = get_object_or_404(manager, pk=pk)
    parent_thread_obj = post_obj.parent_thread

    # Handle private forum
    if not parent_thread_obj.has_access(request.user):
        raise PermissionDenied()

    # Handle closed thread
    if parent_thread_obj.closed or parent_thread_obj.locked:

        # Render the "closed thread" template
        context = {
            'thread': parent_thread_obj,
            'forum': parent_thread_obj.parent_forum,
            'title': _('Thread closed'),
        }
        if extra_context is not None:
            context.update(extra_context)

        return TemplateResponse(request, template_name_closed_thread, context)

    # Handle anti flood
    current_user = request.user
    is_flooding = False

    # Get default notify settings
    notify_of_reply_default = current_user.forum_profile.notify_of_reply_by_default

    # Handle form GET/POST
    if request.method == "POST":

        # Check for flood only on POST
        is_flooding = current_user.forum_profile.is_flooding()

        # Handle form and anti flood
        form = forum_thread_reply_form(request.POST, request.FILES)
        if form.is_valid() and not is_flooding:
            opts = {
                'author': current_user,
                'parent_thread': parent_thread_obj,
                'request': request
            }
            new_post = form.save(**opts)
            return HttpResponseRedirect(new_post.get_absolute_url())
    else:
        quote_content = post_obj.content
        quote_author = post_obj.author
        quote_author_url = quote_author.user_profile.get_absolute_url()
        form = forum_thread_reply_form(initial={'content': render_quote(quote_content,
                                                                        quote_author.username,
                                                                        quote_author_url),
                                                'notify_of_reply': notify_of_reply_default})

    # Render the template
    context = {
        'related_post': post_obj,
        'thread': parent_thread_obj,
        'forum': parent_thread_obj.parent_forum,
        'form': form,
        'title': _('Reply to post'),
        'is_flooding': is_flooding,
        'flood_delay_sec': NB_SECONDS_BETWEEN_POSTS
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_thread_post_edit(request, pk,
                           template_name='forum/forum_thread_post_edit.html',
                           forum_thread_post_edit_form=ForumThreadPostEditForm,
                           extra_context=None):
    """
    Forum thread's post edit view.
    :param request: The current request.
    :param pk: The post PK.
    :param template_name: The template name to be used.
    :param forum_thread_post_edit_form: The form class to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert pk is not None

    # Get the post object by PK
    manager = ForumThreadPost.objects.published().select_related('parent_thread',
                                                                 'parent_thread__parent_forum',
                                                                 'author')
    post_obj = get_object_or_404(manager, pk=pk)
    parent_thread_obj = post_obj.parent_thread

    # Handle private forum
    current_user = request.user
    if not parent_thread_obj.has_access(current_user):
        raise PermissionDenied()

    # Handle edit permission
    current_user = request.user
    if not post_obj.can_edit(current_user):
        raise PermissionDenied()

    # Handle first post (edit thread instead)
    if post_obj.is_first_post():
        return HttpResponseRedirect(parent_thread_obj.get_edit_url())

    # Handle form GET/POST
    if request.method == "POST":
        form = forum_thread_post_edit_form(request.POST, request.FILES, instance=post_obj)
        if form.is_valid():
            opts = {
                'author': current_user,
                'request': request
            }
            form.save(**opts)
            return HttpResponseRedirect(post_obj.get_absolute_url())
    else:
        form = forum_thread_post_edit_form(instance=post_obj)

    # Render the template
    context = {
        'post': post_obj,
        'thread': parent_thread_obj,
        'forum': parent_thread_obj.parent_forum,
        'form': form,
        'title': _('Edit post'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def forum_thread_post_delete(request, pk,
                             template_name='forum/forum_thread_post_delete.html',
                             forum_thread_post_delete_form=ForumThreadPostDeleteForm,
                             extra_context=None):
    """
    Thread post delete view.
    :param request: The current request.
    :param pk: The thread post PK.
    :param template_name: The template name to be used.
    :param forum_thread_post_delete_form: The form class to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """
    assert pk is not None

    # Get the post object by PK
    manager = ForumThreadPost.objects.published().select_related('parent_thread',
                                                                 'parent_thread__parent_forum',
                                                                 'author')
    post_obj = get_object_or_404(manager, pk=pk)
    parent_thread_obj = post_obj.parent_thread

    # Handle private forum
    current_user = request.user
    if not parent_thread_obj.has_access(current_user):
        raise PermissionDenied()

    # Handle delete permission
    current_user = request.user
    if not post_obj.can_delete(current_user):
        raise PermissionDenied()

    # Detect first thread post (special case)
    if post_obj.is_first_post():
        return HttpResponseRedirect(parent_thread_obj.get_delete_url())

    # Handle form GET/POST
    if request.method == "POST":
        form = forum_thread_post_delete_form(request.POST)
        if form.is_valid():
            opts = {
                'post': post_obj,
            }
            form.save(**opts)
            return HttpResponseRedirect(parent_thread_obj.get_absolute_url())
    else:
        form = forum_thread_post_delete_form()

    # Render the template
    context = {
        'post': post_obj,
        'thread': parent_thread_obj,
        'forum': parent_thread_obj.parent_forum,
        'form': form,
        'title': _('Delete post'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
def my_threads_list(request,
                    template_name='forum/forum_mythreads_list.html',
                    extra_context=None):
    """
    Current user's threads list.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the thread list for the current user
    thread_list = ForumThread.objects.published().filter(first_post__author=request.user) \
        .select_related('first_post__author', 'last_post__author')

    # Thread list pagination
    paginator, page = paginate(thread_list, request, NB_FORUM_THREAD_PER_PAGE)

    # Render the template
    context = {
        'title': _('My forum threads list'),
    }
    update_context_for_pagination(context, 'threads', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
def my_posts_list(request,
                  template_name='forum/forum_myposts_list.html',
                  extra_context=None):
    """
    Current user's posts list.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the post list for the current user
    post_list = request.user.forum_posts.published() \
        .select_related('author__user_profile', 'last_modification_by').prefetch_related('attachments')

    # Post list pagination
    paginator, page = paginate(post_list, request, NB_FORUM_POST_PER_PAGE)

    # Render the template
    context = {
        'title': _('My forum posts list'),
    }
    update_context_for_pagination(context, 'posts', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
def my_forums_subscription_list(request,
                                template_name='forum/forum_myforumssubscription_list.html',
                                extra_context=None):
    """
    Current user's forums subscription list.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get all subscriptions
    subscriptions = ForumSubscription.objects.filter(user=request.user, active=True).select_related('forum')

    # Forum subscriptions list pagination
    paginator, page = paginate(subscriptions, request, NB_FORUM_THREAD_PER_PAGE)

    # Render the template
    context = {
        'title': _('My forum subscriptions list'),
    }
    update_context_for_pagination(context, 'forum_subscriptions', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@login_required
def my_threads_subscription_list(request,
                                 template_name='forum/forum_mythreadssubscription_list.html',
                                 extra_context=None):
    """
    Current user's threads subscription list.
    :param request: The current request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get all subscriptions
    subscriptions = ForumThreadSubscription.objects.filter(user=request.user,
                                                           thread__deleted_at__isnull=True, active=True) \
        .select_related('thread__first_post__author', 'thread__last_post__author')

    # Thread subscriptions list pagination
    paginator, page = paginate(subscriptions, request, NB_FORUM_THREAD_PER_PAGE)

    # Render the template
    context = {
        'title': _('My forum thread subscriptions list'),
    }
    update_context_for_pagination(context, 'thread_subscriptions', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@never_cache
@csrf_protect
@login_required
def my_account_show(request,
                    template_name='forum/my_account.html',
                    account_edit_form=ForumProfileModificationForm,
                    post_edit_redirect=None,
                    extra_context=None):
    """
    User forum's account page view, allow modification of forum preferences.
    :param request: The incoming request.
    :param template_name: The template to be used.
    :param account_edit_form: The account edition form class to be used.
    :param post_edit_redirect: The post edit redirect uri or reverse.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse or HttpResponseRedirect
    """

    # Compute the post edit redirect uri
    if post_edit_redirect is None:
        post_edit_redirect = reverse('forum:myaccount')
    else:
        post_edit_redirect = resolve_url(post_edit_redirect)

    # Get the current user profile
    current_user_profile = request.user.forum_profile
    assert current_user_profile is not None  # Just in case

    # Handle the form
    if request.method == "POST":
        form = account_edit_form(request.POST, instance=current_user_profile)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 _('Your forum preferences has been successfully updated!'))
            return HttpResponseRedirect(post_edit_redirect)
    else:
        form = account_edit_form(instance=current_user_profile)

    # Render the template
    context = {
        'form': form,
        'title': _('My forum preferences'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
