"""
Utility class for notifications of the private messages app.
"""

from apps.notifications.models import Notification


def notify_of_new_private_message(private_msg, request,
                                  title_template_name="privatemsg/notif_new_msg_title.txt",
                                  message_template_name="privatemsg/notif_new_msg.txt",
                                  message_template_name_html="privatemsg/notif_new_msg.html",
                                  extra_context=None,
                                  kwargs_send_mail=None):
    """
    Notify recipient of a new private message
    :param private_msg: The new private message instance.
    :param request: The current request.
    :param title_template_name: The template name to be used for the notification's title.
    :param message_template_name: The template name to be used for the notification's message.
    :param message_template_name_html: The template name to be used for the notification's message in HTML format.
    :param extra_context: Any extra context for the template.
    :param kwargs_send_mail: Any extra keywords arguments for the mail function.
    :return: None
    """

    # Do not send notification if not desired
    if not private_msg.recipient.privatemsg_profile.notify_on_new_privmsg:
        return

    # Do not send notifications for self message
    if request.user == private_msg.recipient:
        return

    # Notify recipient of a new private message
    user = private_msg.recipient
    context = {
        'message': private_msg,
        'user': user
    }
    if extra_context is not None:
        context.update(extra_context)
    Notification.objects.send_notification_to_user(request=request, user=user,
                                                   title_template_name=title_template_name,
                                                   message_template_name=message_template_name,
                                                   message_template_name_html=message_template_name_html,
                                                   extra_context=context, kwargs_send_mail=kwargs_send_mail)
