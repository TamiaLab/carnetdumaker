"""
Tests suite for the models of the blog app.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test.utils import override_settings


from ..models import (Article,
                      ArticleRevision,
                      ArticleNote,
                      ArticleTag,
                      ArticleCategory)
from ..constants import NOTE_TYPE_DEFAULT


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
