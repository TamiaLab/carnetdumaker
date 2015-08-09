"""
Utility class for notifications of the bug tracker app.
"""

from apps.notifications.models import Notification

from .models import (IssueTicketSubscription,
                     BugTrackerUserProfile)


def notify_of_new_issue(issue, request, excluded_user,
                        title_template_name="bugtracker/notif_new_issue_title.txt",
                        message_template_name="bugtracker/notif_new_issue_msg.txt",
                        message_template_name_html="bugtracker/notif_new_issue_msg.html",
                        extra_context=None,
                        kwargs_send_mail=None):
    """
    Notify all subscribers of new issue.
    :param issue: The new issue.
    :param request: The current request.
    :param excluded_user: The user to be excluded from the notification list (the issue's author).
    :param title_template_name: The template name to be used for the notification's title.
    :param message_template_name: The template name to be used for the notification's message.
    :param message_template_name_html: The template name to be used for the notification's message in HTML format.
    :param extra_context: Any extra context for the template.
    :param kwargs_send_mail: Any extra keywords arguments for the mail function.
    :return: None
    """

    # Notify all subscribers of a new issue
    for subscriber in BugTrackerUserProfile.objects.get_subscribers_for_new_issue().exclude(user=excluded_user) \
            .select_related('user'):
        user = subscriber.user
        context = {
            'issue': issue,
            'user': user
        }
        if extra_context is not None:
            context.update(extra_context)
        Notification.objects.send_notification_to_user(request=request, user=user,
                                                       title_template_name=title_template_name,
                                                       message_template_name=message_template_name,
                                                       message_template_name_html=message_template_name_html,
                                                       extra_context=context, kwargs_send_mail=kwargs_send_mail)


def notify_of_new_comment(issue, comment, request, excluded_user,
                          title_template_name="bugtracker/notif_new_comment_title.txt",
                          message_template_name="bugtracker/notif_new_comment_msg.txt",
                          message_template_name_html="bugtracker/notif_new_comment_msg.html",
                          extra_context=None,
                          kwargs_send_mail=None):
    """
    Notify all subscribers of new comment.
    :param issue: The parent issue.
    :param comment: The new comment.
    :param request: The current request.
    :param excluded_user: The user to be excluded from the notification list (the comment's author).
    :param title_template_name: The template name to be used for the notification's title.
    :param message_template_name: The template name to be used for the notification's message.
    :param message_template_name_html: The template name to be used for the notification's message in HTML format.
    :param extra_context: Any extra context for the template.
    :param kwargs_send_mail: Any extra keywords arguments for the mail function.
    :return: None
    """

    # Notify all subscribers of a new comment
    for subscriber in IssueTicketSubscription.objects.get_subscribers_for_issue(issue).exclude(user=excluded_user) \
            .select_related('user'):
        user = subscriber.user
        context = {
            'issue': issue,
            'comment': comment,
            'user': user
        }
        if extra_context is not None:
            context.update(extra_context)
        Notification.objects.send_notification_to_user(request=request, user=user,
                                                       title_template_name=title_template_name,
                                                       message_template_name=message_template_name,
                                                       message_template_name_html=message_template_name_html,
                                                       extra_context=context, kwargs_send_mail=kwargs_send_mail)
