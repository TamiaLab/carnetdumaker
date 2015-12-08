"""
Custom template tags for the user accounts app.
"""

from django import template
from django.core.urlresolvers import reverse
from django.utils.html import conditional_escape
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from ..models import UserProfile
from ..settings import (DEFAULT_MAX_NB_USER_IN_LATEST_CREATED_ACCOUNTS_LIST,
                        DEFAULT_MAX_NB_USER_IN_LATEST_MODIFIED_ACCOUNTS_LIST,
                        DEFAULT_MAX_NB_USER_IN_LATEST_ONLINE_ACCOUNTS_LIST)


register = template.Library()


@register.filter(needs_autoescape=True)
def user_profile_link(user, autoescape=True):
    """
    Return a link (safe text) to the given user profile if active.
    If the user is not active, return the string "Anonymous", translated in the current user language.
    If the user is ``None``, return an empty string to avoid template error at runtime.
    :param user: The user to generate the link for.
    :param autoescape: Boolean flag from the Django template engine.
    """
    if user is None:
        return ''
    if user.is_active:
        if autoescape:
            user_username = conditional_escape(user.username)
        else:
            user_username = user.username
        user_profile_url = reverse('accounts:user_profile', kwargs={'username': user_username})
        result = '<a href="{url}">{username}</a>'.format(url=force_text(user_profile_url), username=user_username)
        return mark_safe(result)
    else:
        return _('Anonymous')


@register.assignment_tag
def get_latest_created_user_accounts(max_nb_user=DEFAULT_MAX_NB_USER_IN_LATEST_CREATED_ACCOUNTS_LIST):
    """
    Return a queryset of the N latest created user accounts.
    :param max_nb_user: The maximum number of user accounts to be returned.
    """
    return UserProfile.objects.get_active_users_accounts().select_related('user') \
               .order_by('-user__date_joined')[:max_nb_user]


@register.assignment_tag
def get_latest_modified_user_accounts(max_nb_user=DEFAULT_MAX_NB_USER_IN_LATEST_MODIFIED_ACCOUNTS_LIST):
    """
    Return a queryset of the N latest modified user accounts.
    :param max_nb_user: The maximum number of user accounts to be returned.
    """
    return UserProfile.objects.select_related('user') \
               .order_by('-last_modification_date')[:max_nb_user]


@register.assignment_tag
def get_latest_online_user_accounts(max_nb_user=DEFAULT_MAX_NB_USER_IN_LATEST_ONLINE_ACCOUNTS_LIST):
    """
    Return a queryset of the N latest online user accounts.
    :param max_nb_user: The maximum number of user accounts to be returned.
    """
    return UserProfile.objects.get_online_users_accounts().select_related('user') \
               .order_by('-last_modification_date')[:max_nb_user]
