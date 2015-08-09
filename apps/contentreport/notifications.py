"""
Utility class for notifications of the content report app.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.notifications.models import Notification

from .settings import USERNAME_LIST_FOR_CONTENT_REPORT_NOTIFICATION


def notify_of_new_report(new_report, reporter, request,
                         content_object_name='content_object',
                         title_template_name="contentreport/new_content_report_subject.txt",
                         message_template_name="contentreport/new_content_report_body.txt",
                         message_template_name_html="contentreport/new_content_report_body.html",
                         extra_context=None,
                         kwargs_send_mail=None):
    """
    Notify admin of a new content report.
    :param new_report: The new content report.
    :param reporter: The reporter.
    :param request: The current request.
    :param content_object_name: The content object context variable name for template.
    :param title_template_name: The template name to be used for the notification's title.
    :param message_template_name: The template name to be used for the notification's message.
    :param message_template_name_html: The template name to be used for the notification's message in HTML format.
    :param extra_context: Any extra context for the template.
    :param kwargs_send_mail: Any extra keywords arguments for the mail function.
    :return: None
    """

    # Notify all admin
    for user in get_user_model().objects \
            .filter(Q(username__in=USERNAME_LIST_FOR_CONTENT_REPORT_NOTIFICATION) | Q(is_superuser=True)):
        context = {
            content_object_name: new_report.content_object,
            'report': new_report,
            'reporter': reporter,
            'user': user
        }
        if extra_context is not None:
            context.update(extra_context)
        Notification.objects.send_notification_to_user(request=request, user=user,
                                                       title_template_name=title_template_name,
                                                       message_template_name=message_template_name,
                                                       message_template_name_html=message_template_name_html,
                                                       extra_context=context, kwargs_send_mail=kwargs_send_mail)
