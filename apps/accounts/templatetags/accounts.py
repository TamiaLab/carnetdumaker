"""
Custom template tags for the user accounts app.
"""

from django import template
from django.core.urlresolvers import reverse
from django.utils.html import conditional_escape
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


register = template.Library()


@register.filter(is_safe=True, needs_autoescape=True)
def user_profile_link(user, autoescape=True):
    """
    Return a link (safe text) to the given user profile if active.
    If the user is not active, return the string Anonymous, translate in the current user language.
    :param user: The user to generate the link for.
    :param autoescape: Boolean flag from the Django template engine.
    """
    if user is None:
        return ''
    if autoescape:
        escaper = conditional_escape
    else:
        escaper = lambda x: x
    if user.is_active:
        user_username = escaper(user.username)
        user_profile_url = reverse('accounts:user_profile', kwargs={'username': user_username})
        result = '<a href="{url}">{username}</a>'.format(url=force_text(user_profile_url), username=user_username)
        return mark_safe(result)
    else:
        return _('Anonymous')
