"""
Views for the blog app.
"""

from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponsePermanentRedirect

from apps.paginator.shortcut import (update_context_for_pagination,
                                     paginate)

from .settings import NB_ARTICLES_PER_PAGE
from .models import (Article,
                     ArticleCategory,
                     ArticleTag)


def article_list(request,
               template_name='blog/article_list.html',
               extra_context=None):
    """
    Blog home page view, list all recently published article.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all published articles
    published_articles = Article.objects.published() \
        .select_related('author').prefetch_related('tags', 'categories')

    # Articles list pagination
    paginator, page = paginate(published_articles, request, NB_ARTICLES_PER_PAGE)

    # Render the template
    context = {
        'title': _('Articles'),
    }
    update_context_for_pagination(context, 'articles', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def article_detail(request, slug,
                 template_name='blog/article_detail.html',
                 extra_context=None):
    """
    Detail view for a specific article.
    :param slug: The desired article's slug.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve the article
    manager = Article.objects.select_related('author',
                                             'author__user_profile',
                                             'license',
                                             'related_forum_thread')
    article_obj = get_object_or_404(manager, slug=slug)

    # Handle 404 and 410 here
    if not article_obj.can_see_preview(request.user):
        if article_obj.is_gone():
            context = {
                'title': _('Article lost in cyberspace'),
            }
            return TemplateResponse(request, '410.html', context)
        if not article_obj.is_published():
            raise Http404()

    # Render the template
    context = {
        'article': article_obj,
        'title': article_obj.title,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def article_detail_year_month_day(request, slug, year,
                                month=None, day=None):
    """
    Year/month/day permalink redirect view for an article.
    :param request: The current request.
    :param slug: The article slug.
    :param year: The article's publication year.
    :param month: The article's publication month (optional).
    :param day: The article's publication day (optional).
    :return: HttpResponsePermanentRedirect
    """

    # Retrieve the article
    article_obj = get_object_or_404(Article, slug=slug)

    # Check date to avoid multiple redirection to the same article
    pub_date = article_obj.pub_date
    if int(year) != pub_date.year:
        raise Http404()
    if month is not None and int(month) != pub_date.month:
        raise Http404()
    if day is not None and int(day) != pub_date.day:
        raise Http404()

    # Redirect to the canonical URL
    return HttpResponsePermanentRedirect(article_obj.get_absolute_url())


def tag_list(request,
             template_name='blog/tag_list.html',
             extra_context=None):
    """
    List view of all tags as a "cloud".
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve all tag to create a freaking awesome tag cloud
    queryset = ArticleTag.objects.all()

    # Render the template without pagination
    context = {
        'title': _('Tags list'),
        'tags': queryset,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def tag_detail(request, slug,
             template_name='blog/tag_detail.html',
             extra_context=None):
    """
    Detail view for a specific tag.
    :param slug: The desired tag's slug.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Retrieve the tag
    tag_obj = get_object_or_404(ArticleTag, slug=slug)

    # Related articles list pagination
    paginator, page = paginate(tag_obj.articles.published()
                               .select_related('author').prefetch_related('tags', 'categories'),
                               request, NB_ARTICLES_PER_PAGE)

    # Render the template
    context = {
        'title': _('Tag %s') % tag_obj.name,
        'tag': tag_obj,
    }
    update_context_for_pagination(context, 'related_articles', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def category_list(request,
                  template_name='blog/category_list.html',
                  extra_context=None):
    """
    List view of all root categories.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get all categories (prefetch in order to do iterative templating)
    queryset = ArticleCategory.objects.all().select_related('parent')

    # Render the template without pagination
    context = {
        'title': _('Categories list'),
        'categories': queryset,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def category_detail(request, hierarchy,
                  template_name='blog/category_detail.html',
                  extra_context=None):
    """
    Detail view for a specific category.
    :param hierarchy: The desired category's slug(s) hierarchy.
    :param request: The incoming request.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Get the desired category
    manager = ArticleCategory.objects.select_related('parent')
    category_obj = get_object_or_404(manager, slug_hierarchy=hierarchy)

    # Related articles list pagination
    paginator, page = paginate(category_obj.articles.published()
                               .select_related('author').prefetch_related('tags', 'categories'),
                               request, NB_ARTICLES_PER_PAGE)

    # Render the template
    context = {
        'title': _('Category %s') % category_obj.name,
        'category': category_obj,
    }
    update_context_for_pagination(context, 'related_articles', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def archive_index(request,
                  template_name='blog/archive_index.html',
                  extra_context=None):
    """
    Archive index page.
    :param request:
    :param template_name:
    :param extra_context:
    :return:
    """

    # Get all archive by month
    archive_calendar = Article.objects.published_per_month()

    # Render the template
    context = {
        'title': _('Archives'),
        'archive_calendar': archive_calendar,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def archive_year(request, year,
                 template_name='blog/archive_year.html',
                 extra_context=None):
    """
    Year archive page view, list all article published the given year.
    :param request: The incoming request.
    :param year: The desired archive's year.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Year/month cleaning
    year = int(year)
    if year == 0:
        raise Http404()

    # Retrieve all published articles for the given year
    published_articles = Article.objects.published().filter(pub_date__year=year) \
        .select_related('author').prefetch_related('tags', 'categories')

    # Articles list pagination
    paginator, page = paginate(published_articles, request, NB_ARTICLES_PER_PAGE)

    # Render the template
    context = {
        'title': _('Articles for year %d') % year,
        'year': year,
    }
    update_context_for_pagination(context, 'articles', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def archive_month(request, year, month,
                  template_name='blog/archive_month.html',
                  extra_context=None):
    """
    Year/Month archive page view, list all article published the given year and month.
    :param request: The incoming request.
    :param year: The desired archive's year.
    :param month: The desired archive's month.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: TemplateResponse
    """

    # Year/month cleaning
    year = int(year)
    month = int(month)
    if year == 0 or not 1 <= month <= 12:
        raise Http404()

    # Retrieve all published articles for the given year
    published_articles = Article.objects.published().filter(pub_date__year=year,
                                                            pub_date__month=month) \
        .select_related('author').prefetch_related('tags', 'categories')

    # Articles list pagination
    paginator, page = paginate(published_articles, request, NB_ARTICLES_PER_PAGE)

    # Render the template
    context = {
        'title': _('Articles for %(month)d / %(year)d') % {'year': year, 'month': month},
        'month': month,
        'year': year,
    }
    update_context_for_pagination(context, 'articles', request, paginator, page)
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
