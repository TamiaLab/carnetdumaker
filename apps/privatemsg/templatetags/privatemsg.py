"""
Custom template tags for the private messages app.
"""

from django.template import (Library,
                             Node,
                             TemplateSyntaxError)

from ..models import PrivateMessage


register = Library()


class InboxOutput(Node):
    """
    Template ``Node`` for rendering the ``inbox_count`` template tag.
    """

    def __init__(self, varname=None):
        self.varname = varname

    def render(self, context):
        try:
            user = context['user']
            count = PrivateMessage.objects.inbox_count_for(user)
        except (KeyError, AttributeError):
            count = 0
        if self.varname is not None:
            context[self.varname] = count
            return ''
        else:
            return count


def do_inbox_count(parser, token):
    """
    A template tag to show the unread private messages count for a logged in user.
    Returns the number of unread messages in the user's inbox.
    Usage::
        {% load privatemsg %}
        {% inbox_count %}
        {# or assign the value to a variable: #}
        {% inbox_count as my_var %}
        {{ my_var }}
    """
    bits = token.contents.split()
    if len(bits) > 1:
        if len(bits) != 3:
            raise TemplateSyntaxError("inbox_count tag takes either no arguments or exactly two arguments")
        if bits[1] != 'as':
            raise TemplateSyntaxError("first argument to inbox_count tag must be 'as'")
        return InboxOutput(bits[2])
    else:
        return InboxOutput()


register.tag('inbox_count', do_inbox_count)
