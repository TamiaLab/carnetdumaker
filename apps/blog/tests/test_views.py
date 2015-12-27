"""
Tests suite for the views of the blog app.
"""

from datetime import timedelta, datetime

from django.utils import timezone
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from apps.licenses.models import License

from ..models import (Article,
                      ArticleTag,
                      ArticleCategory)
from ..constants import (ARTICLE_STATUS_DRAFT,
                         ARTICLE_STATUS_PUBLISHED,
                         ARTICLE_STATUS_DELETED)


class BlogViewsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        future_now = now + timedelta(seconds=30)
        self.author = get_user_model().objects.create_user(username='johndoe',
                                                           password='johndoe',
                                                           email='john.doe@example.com')
        self.article_draft = Article.objects.create(title='Test 1',
                                                    slug='test-1',
                                                    author=self.author,
                                                    content='Hello World!',
                                                    status=ARTICLE_STATUS_DRAFT,
                                                    pub_date=now)
        self.article_deleted = Article.objects.create(title='Test 2',
                                                      slug='test-2',
                                                      author=self.author,
                                                      content='Hello World!',
                                                      status=ARTICLE_STATUS_DELETED,
                                                      pub_date=now)
        self.article_published = Article.objects.create(title='Test 3',
                                                        slug='test-3',
                                                        author=self.author,
                                                        content='Hello World!',
                                                        status=ARTICLE_STATUS_PUBLISHED,
                                                        pub_date=now)
        self.article_published_in_future = Article.objects.create(title='Test 4',
                                                                  slug='test-4',
                                                                  author=self.author,
                                                                  content='Hello World!',
                                                                  status=ARTICLE_STATUS_PUBLISHED,
                                                                  pub_date=future_now)
        self.article_expired = Article.objects.create(title='Test 5',
                                                      slug='test-5',
                                                      author=self.author,
                                                      content='Hello World!',
                                                      status=ARTICLE_STATUS_PUBLISHED,
                                                      pub_date=past_now,
                                                      expiration_date=now)

        self.tag = ArticleTag.objects.create(name='Test tag',
                                             slug='test')
        self.article_draft.tags.add(self.tag)
        self.article_deleted.tags.add(self.tag)
        self.article_published.tags.add(self.tag)
        self.article_published_in_future.tags.add(self.tag)
        self.article_expired.tags.add(self.tag)

        self.category = ArticleCategory.objects.create(name='Test category',
                                                       slug='test-category')
        self.article_draft.categories.add(self.category)
        self.article_deleted.categories.add(self.category)
        self.article_published.categories.add(self.category)
        self.article_published_in_future.categories.add(self.category)
        self.article_expired.categories.add(self.category)

    def test_article_list_view_available(self):
        """
        Test the availability of the "article list" view.
        """
        client = Client()
        response = client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_list.html')
        self.assertIn('articles', response.context)
        self.assertQuerysetEqual(response.context['articles'], ['<Article: Test 3>'])

    def test_article_detail_view_available(self):
        """
        Test the availability of the "article detail" view with a published article.
        """
        client = Client()
        response = client.get(self.article_published.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_detail.html')
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'], self.article_published)

    def test_article_detail_view_unavailable_with_unknown_article(self):
        """
        Test the unavailability of the "article detail" view with an unknown article.
        """
        client = Client()
        response = client.get(reverse('blog:article_detail', kwargs={'slug': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_article_detail_view_unavailable_with_unpublished_article(self):
        """
        Test the unavailability of the "article detail" view with an unpublished article.
        """
        client = Client()
        response = client.get(self.article_draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_article_detail_view_unavailable_with_deleted_article(self):
        """
        Test the unavailability of the "article detail" view with an deleted article.
        """
        client = Client()
        response = client.get(self.article_deleted.get_absolute_url())
        self.assertEqual(response.status_code, 410)
        self.assertTemplateUsed(response, '410.html')

    def test_article_detail_view_unavailable_with_expired_article(self):
        """
        Test the unavailability of the "article detail" view with an expired article.
        """
        client = Client()
        response = client.get(self.article_expired.get_absolute_url())
        self.assertEqual(response.status_code, 410)
        self.assertTemplateUsed(response, '410.html')

    def test_article_detail_view_available_in_all_cases_if_authorized(self):
        """
        Test the availability of the "article detail" view with any type of articles if authorized to see them.
        """
        client = Client()
        client.login(username='johndoe', password='johndoe')

        response = client.get(self.article_draft.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_detail.html')
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'], self.article_draft)

        response = client.get(self.article_published.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_detail.html')
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'], self.article_published)

        response = client.get(self.article_deleted.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_detail.html')
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'], self.article_deleted)

        response = client.get(self.article_expired.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_detail.html')
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'], self.article_expired)

    def test_article_detail_year_month_day(self):
        """
        Test the redirection to the article permalink when requesting the URL in format ``year/month/day/slug``.
        """
        client = Client()
        article_url = self.article_published.get_absolute_url()
        pub_date = self.article_published.pub_date

        response = client.get(reverse('blog:article_detail_year_month_day',
                                      kwargs={'year': str(pub_date.year),
                                              'month': '%02d' % pub_date.month,
                                              'day': '%02d' % pub_date.day,
                                              'slug': self.article_published.slug}))
        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, article_url, status_code=301)

        response = client.get(reverse('blog:article_detail_year_month',
                                      kwargs={'year': str(pub_date.year),
                                              'month': '%02d' % pub_date.month,
                                              'slug': self.article_published.slug}))
        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, article_url, status_code=301)

        response = client.get(reverse('blog:article_detail_year',
                                      kwargs={'year': str(pub_date.year),
                                              'slug': self.article_published.slug}))
        self.assertEqual(response.status_code, 301)
        self.assertRedirects(response, article_url, status_code=301)

    def test_article_detail_year_month_day_unavailable_with_unknown_article(self):
        """
        Test the unavailability of the ``year/month/day/slug`` redirection with an unknown article.
        """
        client = Client()
        response = client.get(reverse('blog:article_detail_year', kwargs={'year': '2015', 'slug': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = client.get(reverse('blog:article_detail_year_month', kwargs={'year': '2015',
                                                                                'month': '02',
                                                                                'slug': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = client.get(reverse('blog:article_detail_year_month_day', kwargs={'year': '2015',
                                                                                    'month': '02',
                                                                                    'day': '13',
                                                                                    'slug': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_article_detail_year_month_day_unavailable_with_wrong_pub_date(self):
        """
        Test the unavailability of the ``year/month/day/slug`` redirection with a wrong pub date.
        """
        client = Client()
        pub_date = self.article_published.pub_date

        response = client.get(reverse('blog:article_detail_year_month_day',
                                      kwargs={'year': str(pub_date.year + 1),
                                              'month': '%02d' % pub_date.month,
                                              'day': '%02d' % pub_date.day,
                                              'slug': self.article_published.slug}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = client.get(reverse('blog:article_detail_year_month_day',
                                      kwargs={'year': str(pub_date.year),
                                              'month': '%02d' % (pub_date.month + 1),
                                              'day': '%02d' % pub_date.day,
                                              'slug': self.article_published.slug}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        response = client.get(reverse('blog:article_detail_year_month_day',
                                      kwargs={'year': str(pub_date.year),
                                              'month': '%02d' % pub_date.month,
                                              'day': '%02d' % (pub_date.day + 1),
                                              'slug': self.article_published.slug}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_latest_article_feeds(self):
        """
        Test the availability of the "latest articles" RSS and Atom feeds.
        """
        client = Client()
        response = client.get(reverse('blog:latest_articles_rss'))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse('blog:latest_articles_atom'))
        self.assertEqual(response.status_code, 200)

    def test_tag_list_view_available(self):
        """
        Test the availability of the "tag list" view.
        """
        client = Client()
        response = client.get(reverse('blog:tag_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/tag_list.html')
        self.assertIn('tags', response.context)
        self.assertQuerysetEqual(response.context['tags'], ['<ArticleTag: Test tag>'])

    def test_tag_detail_view_available(self):
        """
        Test the availability of the "tag detail" view.
        """
        client = Client()
        response = client.get(self.tag.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/tag_detail.html')
        self.assertIn('tag', response.context)
        self.assertEqual(response.context['tag'], self.tag)
        self.assertIn('related_articles', response.context)
        self.assertQuerysetEqual(response.context['related_articles'], ['<Article: Test 3>'])

    def test_tag_detail_view_unavailable_with_unknown_tag(self):
        """
        Test the unavailability of the "tag detail" view with an unknown tag.
        """
        client = Client()
        response = client.get(reverse('blog:tag_detail', kwargs={'slug': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_latest_article_for_tag_feeds(self):
        """
        Test the availability of the "latest articles with tag" RSS and Atom feeds.
        """
        client = Client()
        response = client.get(self.tag.get_latest_articles_rss_feed_url())
        self.assertEqual(response.status_code, 200)
        response = client.get(self.tag.get_latest_articles_atom_feed_url())
        self.assertEqual(response.status_code, 200)

    def test_category_list_view_available(self):
        """
        Test the availability of the "category list" view.
        """
        client = Client()
        response = client.get(reverse('blog:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category_list.html')
        self.assertIn('categories', response.context)
        self.assertQuerysetEqual(response.context['categories'], ['<ArticleCategory: Test category>'])

    def test_category_detail_view_available(self):
        """
        Test the availability of the "category detail" view.
        """
        client = Client()
        response = client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category_detail.html')
        self.assertIn('category', response.context)
        self.assertEqual(response.context['category'], self.category)
        self.assertIn('related_articles', response.context)
        self.assertQuerysetEqual(response.context['related_articles'], ['<Article: Test 3>'])

    def test_category_detail_view_unavailable_with_unknown_category(self):
        """
        Test the unavailability of the "category detail" view with an unknown category.
        """
        client = Client()
        response = client.get(reverse('blog:category_detail', kwargs={'hierarchy': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_latest_article_for_category_feeds(self):
        """
        Test the availability of the "latest articles in category" RSS and Atom feeds.
        """
        client = Client()
        response = client.get(self.category.get_latest_articles_rss_feed_url())
        self.assertEqual(response.status_code, 200)
        response = client.get(self.category.get_latest_articles_atom_feed_url())
        self.assertEqual(response.status_code, 200)

    def test_license_articles_detail_view_available(self):
        """
        Test the availability of the "related articles of license detail" view.
        """
        license = License.objects.create(name='License 1', slug='license-1')
        Article.objects.create(title='Test license',
                               slug='test-license',
                               author=self.author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=timezone.now(),
                               license=license)
        client = Client()
        response = client.get(reverse('bloglicense:license_articles_detail', kwargs={'slug': license.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/license_detail.html')
        self.assertIn('license', response.context)
        self.assertEqual(response.context['license'], license)
        self.assertIn('related_articles', response.context)
        self.assertQuerysetEqual(response.context['related_articles'], ['<Article: Test license>'])

    def test_license_articles_feeds_available(self):
        """
        Test the availability of the "related articles of license detail" RSS and Atom feeds.
        """
        license = License.objects.create(name='License 1', slug='license-1')
        Article.objects.create(title='Test license',
                               slug='test-license',
                               author=self.author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=timezone.now(),
                               license=license)
        client = Client()
        response = client.get(reverse('bloglicense:latest_license_articles_rss', kwargs={'slug': license.slug}))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse('bloglicense:latest_license_articles_atom', kwargs={'slug': license.slug}))
        self.assertEqual(response.status_code, 200)

    def test_license_articles_detail_view_unavailable_with_unknown_category(self):
        """
        Test the unavailability of the "related articles of license detail" view with an unknown license.
        """
        client = Client()
        response = client.get(reverse('bloglicense:license_articles_detail', kwargs={'slug': 'unknown'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_archive_index_view_available(self):
        """
        Test the availability of the "archive index" view.
        """
        client = Client()
        pub_date = self.article_published.pub_date
        response = client.get(reverse('blog:archive_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/archive_index.html')
        self.assertIn('archive_calendar', response.context)
        self.assertEqual(response.context['archive_calendar'], [(pub_date.year, [(pub_date.month, 1)])])

    def test_archive_year_view_available(self):
        """
        Test the availability of the "archive for year" view.
        """
        client = Client()
        pub_date = self.article_published.pub_date
        response = client.get(reverse('blog:archive_year', kwargs={'year': str(pub_date.year)}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/archive_year.html')
        self.assertIn('articles', response.context)
        self.assertEqual(list(response.context['articles']), [self.article_published])

    def test_archive_year_view_unavailable_year_zero(self):
        """
        Test the unavailability of the "archive for year" view with a year equal to 0.
        """
        client = Client()
        response = client.get(reverse('blog:archive_year', kwargs={'year': '0000'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_archive_year_view_available_with_unknown_year(self):
        """
        Test the availability of the "archive for year" view with an unknown year of publication.
        """
        client = Client()
        pub_date = self.article_published.pub_date
        response = client.get(reverse('blog:archive_year', kwargs={'year': str(pub_date.year + 1)}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/archive_year.html')
        self.assertIn('articles', response.context)
        self.assertEqual(list(response.context['articles']), [])

    def test_archive_month_view_available(self):
        """
        Test the availability of the "archive for month" view.
        """
        client = Client()
        pub_date = self.article_published.pub_date
        response = client.get(reverse('blog:archive_month', kwargs={'year': str(pub_date.year),
                                                                    'month': '%02d' % pub_date.month}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/archive_month.html')
        self.assertIn('articles', response.context)
        self.assertEqual(list(response.context['articles']), [self.article_published])

    def test_archive_month_view_unavailable_year_zero(self):
        """
        Test the unavailability of the "archive for month" view with a year equal to 0.
        """
        client = Client()
        response = client.get(reverse('blog:archive_month', kwargs={'year': '0000', 'month': '04'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_archive_month_view_unavailable_month_invalid(self):
        """
        Test the unavailability of the "archive for month" view with a month invalid.
        """
        client = Client()
        response = client.get(reverse('blog:archive_month', kwargs={'year': '2015', 'month': '00'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        response = client.get(reverse('blog:archive_month', kwargs={'year': '2015', 'month': '13'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_archive_month_view_available_unknown_month(self):
        """
        Test the availability of the "archive for month" view with an unknown month of publication.
        """
        client = Client()
        pub_date = self.article_published.pub_date
        response = client.get(reverse('blog:archive_month', kwargs={'year': str(pub_date.year + 1),
                                                                    'month': '%02d' % pub_date.month}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/archive_month.html')
        self.assertIn('articles', response.context)
        self.assertEqual(list(response.context['articles']), [])

    def test_archive_month_month_year_filtering(self):
        """
        Test if the view filter by year correctly.
        """
        year_1 = timezone.make_aware(datetime(2014, 4, 1, 12))
        year_2 = timezone.make_aware(datetime(2015, 4, 1, 12))
        Article.objects.create(title='Test a',
                               slug='test-a',
                               author=self.author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=year_1)
        article = Article.objects.create(title='Test b',
                                         slug='test-b',
                                         author=self.author,
                                         content='Hello World!',
                                         status=ARTICLE_STATUS_PUBLISHED,
                                         pub_date=year_2)

        client = Client()
        response = client.get(reverse('blog:archive_month', kwargs={'year': '2015',
                                                                    'month': '04'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/archive_month.html')
        self.assertIn('articles', response.context)
        self.assertEqual(list(response.context['articles']), [article])

    def test_article_archives_feeds(self):
        """
        Test the availability of the "articles archives" RSS and Atom feeds.
        """
        client = Client()
        response = client.get(reverse('blog:articles_archive_year_rss', kwargs={'year': '2015'}))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse('blog:articles_archive_year_rss', kwargs={'year': '2015'}))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse('blog:articles_archive_month_rss', kwargs={'year': '2015', 'month': '02'}))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse('blog:articles_archive_month_rss', kwargs={'year': '2015', 'month': '02'}))
        self.assertEqual(response.status_code, 200)
