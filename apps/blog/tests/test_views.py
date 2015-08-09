"""
Test suite for the views of the blog app.
"""

from django.utils import timezone
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import (Article,
                      ArticleTag,
                      ArticleCategory)
from ..constants import ARTICLE_STATUS_PUBLISHED


class AnnouncementViewsTestCase(TestCase):
    """
    Test suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        now = timezone.now()
        self.author = get_user_model().objects.create_user(username='johndoe',
                                                           password='illpassword',
                                                           email='john.doe@example.com')
        self.a1 = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=self.author,
                                         content='Hello World!',
                                         status=ARTICLE_STATUS_PUBLISHED,
                                         pub_date=now)
        self.t1 = ArticleTag.objects.create(name='test',
                                            slug='test')
        self.c1 = ArticleCategory.objects.create(name='Test category',
                                            slug='test-category')

    def test_articles_list_view_available(self):
        """
        Test the availability of the "articles list" view.
        """
        client = Client()
        response = client.get(reverse('blog:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_list.html')

    def test_article_detail_view_available(self):
        """
        Test the availability of the "article detail" view.
        """
        client = Client()
        response = client.get(self.a1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_detail.html')

    def test_tags_list_view_available(self):
        """
        Test the availability of the "tags list" view.
        """
        client = Client()
        response = client.get(reverse('blog:tag_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/tag_list.html')

    def test_tag_detail_view_available(self):
        """
        Test the availability of the "tag detail" view.
        """
        client = Client()
        response = client.get(self.t1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/tag_detail.html')

    def test_categories_list_view_available(self):
        """
        Test the availability of the "categories list" view.
        """
        client = Client()
        response = client.get(reverse('blog:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category_list.html')

    def test_category_detail_view_available(self):
        """
        Test the availability of the "category detail" view.
        """
        client = Client()
        response = client.get(self.c1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category_detail.html')
