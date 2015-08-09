"""
Tests suite for the template tags of the blog app.
"""

from datetime import timedelta

from django.utils import timezone
from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model

from ..templatetags import blog
from ..models import (Article,
                      ArticleCategory)
from ..constants import ARTICLE_STATUS_PUBLISHED


class BlogTemplateTagsTestCase(SimpleTestCase):
    """
    Tests suite for the template tags of the blog app (part 1/2).
    """

    def test_month_name_valid_month(self):
        """
        Test the ``month_name`` filter with a valid month.
        """
        result = blog.month_name('1')
        self.assertEqual(result, blog.MONTH_NAME[0])
        result = blog.month_name('12')
        self.assertEqual(result, blog.MONTH_NAME[11])

    def test_month_name_invalid_month_not_int(self):
        """
        Test the ``month_name`` filter with an invalid month (not a int).
        """
        result = blog.month_name('a')
        self.assertEqual(result, 'a')

    def test_month_name_invalid_month_below_array(self):
        """
        Test the ``month_name`` filter with an invalid month (not between 1 and 12).
        """
        result = blog.month_name('-1')
        self.assertEqual(result, '-1')
        result = blog.month_name('13')
        self.assertEqual(result, '13')

    def test_month_format_valid_month(self):
        """
        Test the ``month_format`` filter with a valid month.
        """
        result = blog.month_format('1')
        self.assertEqual(result, '01')
        result = blog.month_format('12')
        self.assertEqual(result, '12')

    def test_month_format_invalid_month_not_int(self):
        """
        Test the ``month_format`` filter with an invalid month (not a int).
        """
        result = blog.month_format('a')
        self.assertEqual(result, 'a')

    def test_month_format_invalid_month_below_array(self):
        """
        Test the ``month_format`` filter with an invalid month (not between 1 and 12).
        """
        result = blog.month_format('-1')
        self.assertEqual(result, '-1')
        result = blog.month_format('13')
        self.assertEqual(result, '13')


class BlogTemplateTagsDbTestCase(TestCase):
    """
    Tests suite for the template tags of the blog app (part 2/2, require database).
    """

    def test_recent_articles_list(self):
        """
        Test the result of the ``recent_articles_list`` tag.
        """
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

        result = blog.recent_articles_list()
        self.assertQuerysetEqual(result, ['<Article: Test 2>'])

    def test_recent_articles_list_limit(self):
        """
        Test the result count limiting of the ``recent_articles_list`` tag.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='illpassword',
                                                      email='john.doe@example.com')
        now = timezone.now()
        nb_objects = 5
        excepted_result = []
        for i in range(nb_objects + 1):
            pub_date = now - timedelta(seconds=i)
            Article.objects.create(title='Test %d' % i,
                                   slug='test-%d' % i,
                                   author=author,
                                   content='Hello World!',
                                   status=ARTICLE_STATUS_PUBLISHED,
                                   pub_date=pub_date)
            excepted_result.append('<Article: Test %d>' % i)
        result = blog.recent_articles_list(nb_objects)
        self.assertQuerysetEqual(result, excepted_result[:nb_objects])

    def test_all_categories(self):
        """
        Test the result of the ``all_categories`` tag.
        """
        ArticleCategory.objects.create(name='Test category 1',
                                       slug='test-category-1')
        ArticleCategory.objects.create(name='Test category 2',
                                       slug='test-category-2')
        ArticleCategory.objects.create(name='Test category 3',
                                       slug='test-category-3')

        result = blog.all_categories()
        self.assertQuerysetEqual(result, ['<ArticleCategory: Test category 1>',
                                          '<ArticleCategory: Test category 2>',
                                          '<ArticleCategory: Test category 3>'])
