"""
Custom template tags for the notifications app.
"""

from django.template import (Library,
                             Node,
                             TemplateSyntaxError)

from ..models import Notification


register = Library()


class NotificationsOutput(Node):
    """
    Template ``Node`` for rendering the ``notifications_count`` template tag.
    """

    def __init__(self, varname=None):
        self.varname = varname

    def render(self, context):
        """
        Render the node.
        """
        try:
            user = context['user']
            count = Notification.objects.unread_notifications_count(user)
        except (KeyError, AttributeError):
            count = 0
        if self.varname is not None:
            context[self.varname] = count
            return ''
        else:
            return count


def do_notifications_count(parser, token):
    """
    A template tag to show the unread notifications count for a logged in user.
    Returns the number of unread notifications for the current user account.
    Usage::
        {% load notifications %}
        {% notifications_count %}
        {# or assign the value to a variable: #}
        {% notifications_count as my_var %}
        {{ my_var }}
    """
    bits = token.contents.split()
    if len(bits) > 1:
        if len(bits) != 3:
            raise TemplateSyntaxError("notifications_count tag takes either no arguments or exactly two arguments")
        if bits[1] != 'as':
            raise TemplateSyntaxError("first argument to notifications_count tag must be 'as'")
        return NotificationsOutput(bits[2])
    else:
        return NotificationsOutput()


register.tag('notifications_count', do_notifications_count)
