"""
Tests suite for the sitemap of the blog app.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import (Article,
                      ArticleTag,
                      ArticleCategory)
from ..sitemap import (ArticlesSitemap,
                       ArticleTagsSitemap,
                       ArticleCategoriesSitemap)
from ..constants import ARTICLE_STATUS_PUBLISHED


class ArticlesSitemapTestCase(TestCase):
    """
    Tests suite for the ``ArticlesSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        now = timezone.now()
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=author,
                               content='Hello World!',
                               pub_date=None)
        Article.objects.create(title='Test 2',
                               slug='test-2',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now)
        Article.objects.create(title='Test 3',
                               slug='test-3',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=future_now)

        # Test the resulting sitemap content
        sitemap = ArticlesSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<Article: Test 2>'])

    def test_lastmod(self):
        """
        Test the ``lastmod`` method of the sitemap with an article modified after being published.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        article = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=author,
                                         content='Hello World!',
                                         status=ARTICLE_STATUS_PUBLISHED,
                                         pub_date=now)
        article.title = 'Test 1 - reborn'
        article.save()
        self.assertIsNotNone(article.last_content_modification_date)
        self.assertIsNotNone(article.pub_date)

        # Test the result of the method
        sitemap = ArticlesSitemap()
        self.assertEqual(sitemap.lastmod(article), article.last_content_modification_date)

    def test_lastmod_no_modification(self):
        """
        Test the ``lastmod`` method of the sitemap with an article never modified.
        """

        # Create some test fixtures
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        article = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=author,
                                         content='Hello World!',
                                         status=ARTICLE_STATUS_PUBLISHED,
                                         pub_date=now)
        self.assertIsNone(article.last_content_modification_date)
        self.assertIsNotNone(article.pub_date)

        # Test the result of the method
        sitemap = ArticlesSitemap()
        self.assertEqual(sitemap.lastmod(article), article.pub_date)


class ArticleTagsSitemapTestCase(TestCase):
    """
    Tests suite for the ``ArticleTagsSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        ArticleTag.objects.create(name='Test 1',
                                  slug='test-1')
        ArticleTag.objects.create(name='Test 2',
                                  slug='test-2')
        ArticleTag.objects.create(name='Test 3',
                                  slug='test-3')

        # Test the resulting sitemap content
        sitemap = ArticleTagsSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<ArticleTag: Test 1>',
                                         '<ArticleTag: Test 2>',
                                         '<ArticleTag: Test 3>'], ordered=False)


class ArticleCategoriesSitemapTestCase(TestCase):
    """
    Tests suite for the ``ArticleCategoriesSitemap`` class.
    """

    def test_sitemap_items(self):
        """
        Test the ``items`` method of the sitemap.
        """

        # Create some test fixtures
        ArticleCategory.objects.create(name='Category 1',
                                       slug='category-1')
        ArticleCategory.objects.create(name='Category 2',
                                       slug='category-2')
        ArticleCategory.objects.create(name='Category 3',
                                       slug='category-3')

        # Test the resulting sitemap content
        sitemap = ArticleCategoriesSitemap()
        items = sitemap.items()
        self.assertQuerysetEqual(items, ['<ArticleCategory: Category 1>',
                                         '<ArticleCategory: Category 2>',
                                         '<ArticleCategory: Category 3>'], ordered=False)
