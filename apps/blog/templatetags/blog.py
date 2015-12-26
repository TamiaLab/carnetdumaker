"""
Custom template tags for the blog app.
"""

from django import template
from django.utils.translation import ugettext_lazy as _

from ..models import (Article,
                      ArticleCategory)
from ..settings import NB_ARTICLES_PER_PAGE_WIDGET


register = template.Library()


MONTH_NAME = (
    _('January'),
    _('February'),
    _('March'),
    _('April'),
    _('May'),
    _('June'),
    _('July'),
    _('August'),
    _('September'),
    _('October'),
    _('November'),
    _('December'),
)


@register.filter
def month_name(month):
    """
    Return the month's name in the current locale.
    :param month: The month number (1 based) to localize.
    :return The month's name in the current locale.
    """
    try:
        month = int(month)
        if month < 1 or month > 12:
            return str(month)
        return MONTH_NAME[month - 1]
    except ValueError:
        return month


@register.filter
def month_format(month):
    """
    Return the given month in the %02d format.
    :param month: The month number to be formatted.
    :return: The month number in the %02d format.
    """
    try:
        month = int(month)
        if month < 1 or month > 12:
            return str(month)
        return '%02d' % month
    except ValueError:
        return month


@register.assignment_tag
def recent_articles_list(nb_objects=NB_ARTICLES_PER_PAGE_WIDGET):
    """
    Returns a list of all N recently published articles.
    :param nb_objects: The maximum number of objects to be returned.
    :return: A list of all N recently published articles.
    """
    return Article.objects.published() \
        .select_related('author').prefetch_related('tags', 'categories')[:nb_objects]


@register.assignment_tag
def all_categories():
    """
    Return a queryset with all ``ArticleCategory`` in database.
    """
    return ArticleCategory.objects.all()
