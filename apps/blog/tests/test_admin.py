"""
Tests suite for the admin views of the blog app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import (Article,
                      ArticleRevision,
                      ArticleNote,
                      ArticleTag,
                      ArticleCategory)


class ArticleAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_superuser(username='johndoe',
                                                                password='illpassword',
                                                                email='john.doe@example.com')
        self.article = Article.objects.create(title='Test 1',
                                              slug='test-1',
                                              author=self.author,
                                              content='Hello World!')
        self.article.content = 'Hello fucking world!'
        self.article.save(current_user=self.author,
                          minor_change=False,
                          revision_description='Test revision')

        # Test for inline image
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=self.author,
                               content='Hello World!',
                               heading_img='fixtures/mea.jpg',
                               thumbnail_img='fixtures/mea.jpg')

    def test_article_list_view_available(self):
        """
        Test the availability of the "article list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_article_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_article_edit_view_available(self):
        """
        Test the availability of the "edit article" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_article_change', args=[self.article.pk]))
        self.assertEqual(response.status_code, 200)

    def test_article_revision_view_available(self):
        client = Client()
        client.login(username='johndoe', password='illpassword')
        self.assertEqual(ArticleRevision.objects.count(), 1)
        revision = ArticleRevision.objects.last()
        response = client.get(reverse('admin:blog_article_show_rev_diff', args=[revision.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/admin_show_rev_diff.html')

    def test_article_revision_view_unavailable_with_nx_revision(self):
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_article_show_rev_diff', args=['1337']))
        self.assertEqual(response.status_code, 404)


class ArticleNoteAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_superuser(username='johndoe',
                                                                password='illpassword',
                                                                email='john.doe@example.com')
        self.note = ArticleNote.objects.create(title_internal='test-no-title',
                                               title='',
                                               description='Test note')
        ArticleNote.objects.create(title_internal='test-with-title',
                                   title='Insert title here',
                                   description='Test note')

    def test_article_note_list_view_available(self):
        """
        Test the availability of the "article note list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_articlenote_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_article_note_edit_view_available(self):
        """
        Test the availability of the "edit article" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_articlenote_change', args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)


class ArticleTagAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_superuser(username='johndoe',
                                                                password='illpassword',
                                                                email='john.doe@example.com')
        self.tag = ArticleTag.objects.create(name='test',
                                             slug='test')

    def test_article_tag_list_view_available(self):
        """
        Test the availability of the "article tag list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_articletag_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_article_tag_edit_view_available(self):
        """
        Test the availability of the "edit article tag" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_articletag_change', args=[self.tag.pk]))
        self.assertEqual(response.status_code, 200)


class ArticleCategoryAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.author = get_user_model().objects.create_superuser(username='johndoe',
                                                                password='illpassword',
                                                                email='john.doe@example.com')
        self.category = ArticleCategory.objects.create(name='Test category',
                                                       slug='test-category')
        ArticleCategory.objects.create(name='Test category',
                                       slug='test-category',
                                       logo='fixtures/mea.jpg')

    def test_article_category_list_view_available(self):
        """
        Test the availability of the "article category list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_articlecategory_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_article_category_edit_view_available(self):
        """
        Test the availability of the "edit article category" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:blog_articlecategory_change', args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
