"""
Utility class for notifications of the forum app.
"""

from apps.notifications.models import Notification

from .models import (ForumSubscription,
                     ForumThreadSubscription)


def notify_of_new_forum_thread(forum_thread, request, excluded_user,
                               title_template_name="forum/notif_new_thread_title.txt",
                               message_template_name="forum/notif_new_thread_msg.txt",
                               message_template_name_html="forum/notif_new_thread_msg.html",
                               extra_context=None,
                               kwargs_send_mail=None):
    """
    Notify subscribers of a new forum's thread.
    :param request: The current request.
    :param title_template_name: The template name to be used for the notification's title.
    :param message_template_name: The template name to be used for the notification's message.
    :param message_template_name_html: The template name to be used for the notification's message in HTML format.
    :param extra_context: Any extra context for the template.
    :param kwargs_send_mail: Any extra keywords arguments for the mail function.
    :return: None
    """

    # Notify all subscribers of a new issue
    for subscriber in ForumSubscription.objects.get_subscribers_for_forum(forum_thread.parent_forum) \
            .exclude(user=excluded_user).select_related('user'):
        user = subscriber.user
        context = {
            'forum': forum_thread.parent_forum,
            'thread': forum_thread,
            'user': user
        }
        if extra_context is not None:
            context.update(extra_context)
        Notification.objects.send_notification_to_user(request=request, user=user,
                                                       title_template_name=title_template_name,
                                                       message_template_name=message_template_name,
                                                       message_template_name_html=message_template_name_html,
                                                       extra_context=context, kwargs_send_mail=kwargs_send_mail)


def notify_of_new_thread_post(new_post, request, excluded_user,
                              title_template_name="forum/notif_new_post_title.txt",
                              message_template_name="forum/notif_new_post_msg.txt",
                              message_template_name_html="forum/notif_new_post_msg.html",
                              extra_context=None,
                              kwargs_send_mail=None):
    """
    Notify subscribers of a new forum thread's post.
    :param request: The current request.
    :param title_template_name: The template name to be used for the notification's title.
    :param message_template_name: The template name to be used for the notification's message.
    :param message_template_name_html: The template name to be used for the notification's message in HTML format.
    :param extra_context: Any extra context for the template.
    :param kwargs_send_mail: Any extra keywords arguments for the mail function.
    :return: None
    """

    # Notify all subscribers of a new issue
    for subscriber in ForumThreadSubscription.objects.get_subscribers_for_thread(new_post.parent_thread) \
            .exclude(user=excluded_user).select_related('user'):
        user = subscriber.user
        context = {
            'thread': new_post.parent_thread,
            'post': new_post,
            'user': user
        }
        if extra_context is not None:
            context.update(extra_context)
        Notification.objects.send_notification_to_user(request=request, user=user,
                                                       title_template_name=title_template_name,
                                                       message_template_name=message_template_name,
                                                       message_template_name_html=message_template_name_html,
                                                       extra_context=context, kwargs_send_mail=kwargs_send_mail)
