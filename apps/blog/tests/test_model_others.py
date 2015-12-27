"""
Tests suite for the models of the blog app.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.test.utils import override_settings


from ..models import (Article,
                      ArticleRevision,
                      ArticleNote,
                      ArticleTag,
                      ArticleCategory,
                      ArticleTwitterCrossPublication)
from ..constants import (NOTE_TYPE_DEFAULT,
                         ARTICLE_STATUS_PUBLISHED)


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticleRevisionTestCase(TestCase):
    """
    Tests suite for the ``ArticleRevision`` data model class.
    """

    def _get_revision(self):
        """
        Create a new article revision with only required attributes set.
        :return: The newly created article revision instance.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        article = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=author,
                                         content='Hello World!')
        revision = ArticleRevision.objects.create(related_article=article,
                                                  title='Revision test',
                                                  content='Hello World!')
        return revision

    def test_default_values(self):
        """
        Test default values of the newly created revision.
        """
        revision = self._get_revision()
        self.assertEqual('', revision.subtitle)
        self.assertEqual('', revision.description)
        self.assertFalse(revision.revision_minor_change)
        self.assertEqual('', revision.revision_description)
        self.assertIsNone(revision.revision_author)
        self.assertIsNotNone(revision.revision_date)

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        revision = self._get_revision()
        self.assertEqual('Revision #%d' % revision.id, str(revision))


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticleNoteTestCase(TestCase):
    """
    Tests suite for the ``ArticleNote`` data model class.
    """

    def _get_note(self):
        """
        Create a new article note with only required attributes set.
        :return: The newly created article note instance.
        """
        note = ArticleNote.objects.create(title_internal='Test 1',
                                          description='Hello World!')
        return note

    def test_default_values(self):
        """
        Test default values of the newly created note.
        """
        note = self._get_note()
        self.assertEqual('', note.title)
        self.assertEqual(NOTE_TYPE_DEFAULT, note.type)

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        note = self._get_note()
        self.assertEqual(note.title_internal, str(note))


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticleTagTestCase(TestCase):
    """
    Tests suite for the ``ArticleTag`` data model class.
    """

    def _get_tag(self):
        """
        Create a new article tag with only required attributes set.
        :return: The newly created article tag instance.
        """
        tag = ArticleTag.objects.create(name='Test 1',
                                        slug='test-1')
        return tag

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        tag = self._get_tag()
        self.assertEqual(tag.name, str(tag))

    def test_get_absolute_url_method(self):
        """
        Test ``get_absolute_url`` method with a valid article tag.
        """
        tag = self._get_tag()
        excepted_url = reverse('blog:tag_detail', kwargs={'slug': tag.slug})
        self.assertEqual(excepted_url, tag.get_absolute_url())

    def test_get_latest_articles_rss_feed_url_method(self):
        """
        Test ``get_latest_articles_rss_feed_url`` method with a valid article tag.
        """
        tag = self._get_tag()
        excepted_url = reverse('blog:latest_tag_articles_rss', kwargs={'slug': tag.slug})
        self.assertEqual(excepted_url, tag.get_latest_articles_rss_feed_url())

    def test_get_latest_articles_atom_feed_url_method(self):
        """
        Test ``get_latest_articles_atom_feed_url`` method with a valid article tag.
        """
        tag = self._get_tag()
        excepted_url = reverse('blog:latest_tag_articles_atom', kwargs={'slug': tag.slug})
        self.assertEqual(excepted_url, tag.get_latest_articles_atom_feed_url())

    def test_slug_unique(self):
        """
        Test if the ``save()`` method handle non-unique slug.
        """
        tag1 = ArticleTag.objects.create(name='Test 1',
                                         slug='test-1')
        tag2 = ArticleTag.objects.create(name='Test 2',
                                         slug='test-1')
        tag3 = ArticleTag.objects.create(name='Test 3',
                                         slug='test-1')
        self.assertNotEqual(tag1.slug, tag2.slug)
        self.assertNotEqual(tag2.slug, tag3.slug)
        self.assertNotEqual(tag1.slug, tag3.slug)


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticleCategoryTestCase(TestCase):
    """
    Tests suite for the ``ArticleCategory`` data model class.
    """

    def _get_category(self):
        """
        Create a new article category with only required attributes set.
        :return: The newly created article category instance.
        """
        category = ArticleCategory.objects.create(name='Test 1',
                                                  slug='test-1')
        return category

    def test_default_values(self):
        """
        Test default values of the newly created category.
        """
        category = self._get_category()
        self.assertIsNone(category.parent)
        self.assertIsNone(category.logo.name)
        self.assertEqual('', category.description)

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        category = self._get_category()
        self.assertEqual(category.name, str(category))

    def test_get_absolute_url_method(self):
        """
        Test ``get_absolute_url`` method with a valid article category.
        """
        category = self._get_category()
        excepted_url = reverse('blog:category_detail', kwargs={'hierarchy': category.slug_hierarchy})
        self.assertEqual(excepted_url, category.get_absolute_url())

    def test_get_latest_articles_rss_feed_url_method(self):
        """
        Test ``get_latest_articles_rss_feed_url`` method with a valid article category.
        """
        category = self._get_category()
        excepted_url = reverse('blog:latest_category_articles_rss', kwargs={'hierarchy': category.slug_hierarchy})
        self.assertEqual(excepted_url, category.get_latest_articles_rss_feed_url())

    def test_get_latest_articles_atom_feed_url_method(self):
        """
        Test ``get_latest_articles_atom_feed_url`` method with a valid article category.
        """
        category = self._get_category()
        excepted_url = reverse('blog:latest_category_articles_atom', kwargs={'hierarchy': category.slug_hierarchy})
        self.assertEqual(excepted_url, category.get_latest_articles_atom_feed_url())

    def test_slug_unique(self):
        """
        Test if the ``save()`` method handle non-unique slug.
        """
        category1 = ArticleCategory.objects.create(name='Test 1',
                                                   slug='test-1')
        category2 = ArticleCategory.objects.create(name='Test 2',
                                                   slug='test-1')
        category3 = ArticleCategory.objects.create(name='Test 3',
                                                   slug='test-1')
        self.assertNotEqual(category1.slug, category2.slug)
        self.assertNotEqual(category2.slug, category3.slug)
        self.assertNotEqual(category1.slug, category3.slug)

    def test_slug_unique_same_parent(self):
        """
        Test if the ``save()`` method handle non-unique slug with same parent.
        """
        parent = ArticleCategory.objects.create(name='Parent category',
                                                slug='parent-cat')
        category1 = ArticleCategory.objects.create(parent=parent,
                                                   name='Test 1',
                                                   slug='test-1')
        category2 = ArticleCategory.objects.create(parent=parent,
                                                   name='Test 2',
                                                   slug='test-1')
        category3 = ArticleCategory.objects.create(parent=parent,
                                                   name='Test 3',
                                                   slug='test-1')
        self.assertNotEqual(category1.slug, category2.slug)
        self.assertNotEqual(category2.slug, category3.slug)
        self.assertNotEqual(category1.slug, category3.slug)

    def test_slug_unique_different_parents(self):
        """
        Test if the ``save()`` method handle non-unique slug but with different parent.
        """
        parent1 = ArticleCategory.objects.create(name='Parent 1',
                                                 slug='parent-1')
        category1 = ArticleCategory.objects.create(parent=parent1,
                                                   name='Test 1',
                                                   slug='test-1')

        parent2 = ArticleCategory.objects.create(name='Parent 1',
                                                 slug='parent-1')
        category2 = ArticleCategory.objects.create(parent=parent2,
                                                   name='Test 2',
                                                   slug='test-1')

        parent3 = ArticleCategory.objects.create(name='Parent 1',
                                                 slug='parent-1')
        category3 = ArticleCategory.objects.create(parent=parent3,
                                                   name='Test 3',
                                                   slug='test-1')
        self.assertEqual(category1.slug, category2.slug)
        self.assertEqual(category2.slug, category3.slug)
        self.assertEqual(category1.slug, category3.slug)

    def test_build_slug_hierarchy_no_parent(self):
        """
        Test if the ``build_slug_hierarchy`` method work as excepted with no parent category.
        """
        category = ArticleCategory(slug='test')
        category.build_slug_hierarchy()
        self.assertEqual('test', category.slug_hierarchy)

    def test_build_slug_hierarchy_parent(self):
        """
        Test if the ``build_slug_hierarchy`` method work as excepted with a parent category.
        """
        parent = ArticleCategory.objects.create(name='Parent category',
                                                slug='parent')
        category = ArticleCategory(parent=parent,
                                   slug='test')
        category.build_slug_hierarchy()
        self.assertEqual('parent/test', category.slug_hierarchy)

    def test_auto_build_slug_hierarchy_on_parent_save(self):
        """
        Test if the ``build_slug_hierarchy`` method is called when a parent category is modified.
        """
        parent = ArticleCategory.objects.create(name='Parent category',
                                                slug='parent')
        child = ArticleCategory.objects.create(parent=parent,
                                               name='Child category',
                                               slug='child')
        leaf = ArticleCategory.objects.create(parent=child,
                                              name='Leaf category',
                                              slug='leaf')
        self.assertEqual('parent', parent.slug_hierarchy)
        self.assertEqual('parent/child', child.slug_hierarchy)
        self.assertEqual('parent/child/leaf', leaf.slug_hierarchy)

        parent.slug = 'new-parent'
        parent.save()
        child.refresh_from_db()
        leaf.refresh_from_db()
        self.assertEqual('new-parent', parent.slug_hierarchy)
        self.assertEqual('new-parent/child', child.slug_hierarchy)
        self.assertEqual('new-parent/child/leaf', leaf.slug_hierarchy)

        child.slug = 'new-child'
        child.save()
        parent.refresh_from_db()
        leaf.refresh_from_db()
        self.assertEqual('new-parent', parent.slug_hierarchy)
        self.assertEqual('new-parent/new-child', child.slug_hierarchy)
        self.assertEqual('new-parent/new-child/leaf', leaf.slug_hierarchy)

        leaf.slug = 'new-leaf'
        leaf.save()
        parent.refresh_from_db()
        child.refresh_from_db()
        self.assertEqual('new-parent', parent.slug_hierarchy)
        self.assertEqual('new-parent/new-child', child.slug_hierarchy)
        self.assertEqual('new-parent/new-child/new-leaf', leaf.slug_hierarchy)


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticleTwitterCrossPublicationTestCase(TestCase):
    """
    Tests suite for the ``ArticleTwitterCrossPublication`` data model.
    """

    def test_str_method(self):
        """
        Test ``__str__`` result for other tests.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        article = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=author,
                                         content='Hello World!')
        tweet = ArticleTwitterCrossPublication.objects.create(article=article,
                                                              tweet_id='0123456789')
        self.assertEqual('%s -> %s' % (article, '0123456789'), str(tweet))

    def test_publish_pending_articles(self):
        """
        Test the ``publish_pending_articles`` method of the manager.
        """

        # Create some test fixtures
        now = timezone.now()
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        article_unpublished = Article.objects.create(title='Test 1',
                                                     slug='test-1',
                                                     author=author,
                                                     content='Hello World!',
                                                     pub_date=None)
        article_published = Article.objects.create(title='Test 2',
                                                   slug='test-2',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now,
                                                   network_publish=False,
                                                   status=ARTICLE_STATUS_PUBLISHED)
        article_published_network = Article.objects.create(title='Test 4',
                                                           slug='test-4',
                                                           author=author,
                                                           content='Hello World!',
                                                           pub_date=now,
                                                           network_publish=True,
                                                           status=ARTICLE_STATUS_PUBLISHED)
        article_published_in_future = Article.objects.create(title='Test 3',
                                                             slug='test-3',
                                                             author=author,
                                                             content='Hello World!',
                                                             pub_date=future_now,
                                                             network_publish=True,
                                                             status=ARTICLE_STATUS_PUBLISHED)
        self.assertIsNotNone(article_unpublished)
        self.assertIsNotNone(article_published)
        self.assertIsNotNone(article_published_network)
        self.assertIsNotNone(article_published_in_future)

        with patch('apps.blog.managers.publish_article_on_twitter') as mock:
            mock.return_value = '0123456789'
            ArticleTwitterCrossPublication.objects.publish_pending_articles()

        self.assertEqual(1, mock.call_count)
        mock.assert_any_call(article_published_network)

        tweets = ArticleTwitterCrossPublication.objects.all()
        self.assertQuerysetEqual(tweets, ['<ArticleTwitterCrossPublication: Test 4 -> 0123456789>'])

    def test_publish_pending_articles_error(self):
        """
        Test the ``publish_pending_articles`` method of the manager when the Twitter api fail.
        """

        # Create some test fixtures
        now = timezone.now()
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        article_unpublished = Article.objects.create(title='Test 1',
                                                     slug='test-1',
                                                     author=author,
                                                     content='Hello World!',
                                                     pub_date=None)
        article_published = Article.objects.create(title='Test 2',
                                                   slug='test-2',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now,
                                                   network_publish=False,
                                                   status=ARTICLE_STATUS_PUBLISHED)
        article_published_network = Article.objects.create(title='Test 4',
                                                           slug='test-4',
                                                           author=author,
                                                           content='Hello World!',
                                                           pub_date=now,
                                                           network_publish=True,
                                                           status=ARTICLE_STATUS_PUBLISHED)
        article_published_in_future = Article.objects.create(title='Test 3',
                                                             slug='test-3',
                                                             author=author,
                                                             content='Hello World!',
                                                             pub_date=future_now,
                                                             network_publish=False,
                                                             status=ARTICLE_STATUS_PUBLISHED)
        self.assertIsNotNone(article_unpublished)
        self.assertIsNotNone(article_published)
        self.assertIsNotNone(article_published_network)
        self.assertIsNotNone(article_published_in_future)

        with patch('apps.blog.managers.publish_article_on_twitter') as mock:
            mock.return_value = False
            ArticleTwitterCrossPublication.objects.publish_pending_articles()

        self.assertEqual(1, mock.call_count)
        mock.assert_any_call(article_published_network)

        tweets = ArticleTwitterCrossPublication.objects.all()
        self.assertQuerysetEqual(tweets, [])

    def test_publish_pending_articles_with_already_posted(self):
        """
        Test the ``publish_pending_articles`` method of the manager when some announcements are already posted.
        """

        # Create some test fixtures
        now = timezone.now()
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        article_unpublished = Article.objects.create(title='Test 1',
                                                     slug='test-1',
                                                     author=author,
                                                     content='Hello World!',
                                                     pub_date=None)
        article_published = Article.objects.create(title='Test 2',
                                                   slug='test-2',
                                                   author=author,
                                                   content='Hello World!',
                                                   pub_date=now,
                                                   network_publish=True,
                                                   status=ARTICLE_STATUS_PUBLISHED)
        article_published2 = Article.objects.create(title='Test 3',
                                                    slug='test-3',
                                                    author=author,
                                                    content='Hello World!',
                                                    pub_date=now,
                                                    network_publish=True,
                                                    status=ARTICLE_STATUS_PUBLISHED)
        article_published_in_future = Article.objects.create(title='Test 4',
                                                             slug='test-4',
                                                             author=author,
                                                             content='Hello World!',
                                                             pub_date=future_now,
                                                             network_publish=True,
                                                             status=ARTICLE_STATUS_PUBLISHED)
        article_published3 = Article.objects.create(title='Test 5',
                                                    slug='test-5',
                                                    author=author,
                                                    content='Hello World!',
                                                    pub_date=now,
                                                    network_publish=False,
                                                    status=ARTICLE_STATUS_PUBLISHED)
        self.assertIsNotNone(article_unpublished)
        self.assertIsNotNone(article_published)
        self.assertIsNotNone(article_published2)
        self.assertIsNotNone(article_published3)
        self.assertIsNotNone(article_published_in_future)

        ArticleTwitterCrossPublication.objects.create(article=article_published,
                                                      tweet_id='0123456789')

        with patch('apps.blog.managers.publish_article_on_twitter') as mock:
            mock.return_value = '0123456789'
            ArticleTwitterCrossPublication.objects.publish_pending_articles()

        self.assertEqual(1, mock.call_count)
        mock.assert_any_call(article_published2)

        tweets = ArticleTwitterCrossPublication.objects.all()
        print(tweets)
        self.assertQuerysetEqual(tweets, ['<ArticleTwitterCrossPublication: Test 2 -> 0123456789>',
                                          '<ArticleTwitterCrossPublication: Test 3 -> 0123456789>'], ordered=False)
