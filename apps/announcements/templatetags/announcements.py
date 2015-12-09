"""
Custom template tags for the announcements app.
"""

from django import template

from ..models import Announcement
from ..settings import NB_ANNOUNCEMENTS_PER_PAGE_WIDGET


register = template.Library()


@register.inclusion_tag('announcements/announcement_list_widget.html')
def recent_announcements(nb_objects=NB_ANNOUNCEMENTS_PER_PAGE_WIDGET):
    """
    Display a list of all N recently published announcements.
    :param nb_objects: The maximum number of objects to be displayed.
    """
    announcement_list = Announcement.objects.published() \
                            .select_related('author').prefetch_related('tags')[:nb_objects]
    return {
        'announcements': announcement_list
    }


@register.assignment_tag
def recent_announcements_list(nb_objects=NB_ANNOUNCEMENTS_PER_PAGE_WIDGET):
    """
    Returns a list of all N recently published announcements.
    :param nb_objects: The maximum number of objects to be returned.
    :return: A list of all N recently published announcements.
    """
    return Announcement.objects.published() \
               .select_related('author').prefetch_related('tags')[:nb_objects]


@register.inclusion_tag('announcements/announcement_list_widget.html')
def global_announcements():
    """
    Display a list of all published site-wide announcements.
    """
    announcement_list = Announcement.objects.published_site_wide() \
        .select_related('author').prefetch_related('tags')
    return {
        'announcements': announcement_list
    }

@register.assignment_tag
def global_announcements_list():
    """
    Returns a list of all N published site-wide announcements.
    """
    return Announcement.objects.published_site_wide() \
        .select_related('author').prefetch_related('tags').all()
