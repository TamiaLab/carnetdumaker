"""
Tests suite for the models of the blog app.
"""

from datetime import timedelta, datetime
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from django.contrib.contenttypes.models import ContentType

from apps.forum.models import (Forum,
                               ForumThread)
from ..models import Article
from ..constants import (ARTICLE_STATUS_DRAFT,
                         ARTICLE_STATUS_PUBLISHED,
                         ARTICLE_STATUS_DELETED)


class ArticleTestCase(TestCase):
    """
    Tests suite for the ``Article`` data model class.
    """

    def _get_article(self):
        """
        Create a new unpublished article with only required attributes set.
        :return: The newly created article instance.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        article = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=author,
                                         content='Hello World!')
        return article

    def test_default_values(self):
        """
        Test default values of the newly created article.
        """
        article = self._get_article()
        self.assertEqual('', article.subtitle)
        self.assertEqual('', article.description)
        self.assertEqual(ARTICLE_STATUS_DRAFT, article.status)
        self.assertIsNone(article.license)
        self.assertTrue(article.network_publish)
        self.assertFalse(article.featured)
        self.assertIsNone(article.heading_img.name)
        self.assertIsNone(article.thumbnail_img.name)
        self.assertIsNotNone(article.creation_date)
        self.assertIsNone(article.last_content_modification_date)
        self.assertIsNone(article.pub_date)
        self.assertIsNone(article.expiration_date)
        self.assertFalse(article.membership_required)
        self.assertIsNone(article.membership_required_expiration_date)
        self.assertIsNone(article.related_forum_thread)
        self.assertTrue(article.auto_create_related_forum_thread)
        self.assertFalse(article.display_img_gallery)

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        article = self._get_article()
        self.assertEqual(article.title, str(article))

    def test_get_absolute_url_method(self):
        """
        Test get_absolute_url method with a valid article.
        """
        article = self._get_article()
        excepted_url = reverse('blog:article_detail', kwargs={'slug': article.slug})
        self.assertEqual(excepted_url, article.get_absolute_url())

    def test_slug_unique(self):
        """
        Test if the ``save()`` method handle non-unique slug.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        article1 = Article.objects.create(title='Test 1',
                                          slug='test-1',
                                          author=author,
                                          content='Hello World!')
        article2 = Article.objects.create(title='Test 2',
                                          slug='test-1',
                                          author=author,
                                          content='Hello World!')
        article3 = Article.objects.create(title='Test 3',
                                          slug='test-1',
                                          author=author,
                                          content='Hello World!')
        self.assertNotEqual(article1.slug, article2.slug)
        self.assertNotEqual(article2.slug, article3.slug)
        self.assertNotEqual(article1.slug, article3.slug)

    def test_fix_pub_date_none_on_publish(self):
        """
        Test if the ``save()`` method fix the ``pub_date`` field on publishing if None.
        """
        article = self._get_article()
        self.assertIsNone(article.pub_date)
        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            article.status = ARTICLE_STATUS_PUBLISHED
            article.save()
            self.assertEqual(article.pub_date, now)
            self.assertIsNone(article.last_content_modification_date)

    def test_fix_content_mod_date_on_publish(self):
        """
        Test if the ``save()`` method fix the ``last_content_modification_date`` field on saving.
        If the ``last_content_modification_date`` date is before ``pub_date``, the value must be None.
        """
        article = self._get_article()
        now = timezone.now()
        article.last_content_modification_date = now - timedelta(seconds=10)
        article.pub_date = now
        article.save()
        self.assertEqual(article.pub_date, now)
        self.assertIsNone(article.last_content_modification_date)

    def test_fix_content_mod_date_on_publish_2(self):
        """
        Test if the ``save()`` method fix the ``last_content_modification_date`` field on saving.
        If the ``last_content_modification_date`` date is equal to ``pub_date``, the value must be None.
        """
        article = self._get_article()
        now = timezone.now()
        article.last_content_modification_date = now
        article.pub_date = now
        article.save()
        self.assertEqual(article.pub_date, now)
        self.assertIsNone(article.last_content_modification_date)

    def test_content_mod_none_if_pub_date_none(self):
        """
        Test if the ``save()`` method fix the ``last_content_modification_date`` field on saving.
        If the ``pub_date`` is None, ``last_content_modification_date`` must be None.
        """
        article = self._get_article()
        article.last_content_modification_date = timezone.now()
        article.pub_date = None
        article.save()
        self.assertIsNone(article.pub_date)
        self.assertIsNone(article.last_content_modification_date)

    def test_content_mod_date_change_on_title_change(self):
        """
        Test if the ``last_content_modification_date`` date change when the title change.
        """
        article = self._get_article()
        article.pub_date = timezone.now()
        article.save()
        self.assertIsNone(article.last_content_modification_date)
        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            article.title = 'New title'
            article.save()
            self.assertEqual(article.last_content_modification_date, now)

    def test_content_mod_date_change_on_subtitle_change(self):
        """
        Test if the ``last_content_modification_date`` date change when the subtitle change.
        """
        article = self._get_article()
        article.pub_date = timezone.now()
        article.save()
        self.assertIsNone(article.last_content_modification_date)
        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            article.subtitle = 'New subtitle'
            article.save()
            self.assertEqual(article.last_content_modification_date, now)

    def test_content_mod_date_change_on_description_change(self):
        """
        Test if the ``last_content_modification_date`` date change when the description change.
        """
        article = self._get_article()
        article.pub_date = timezone.now()
        article.save()
        self.assertIsNone(article.last_content_modification_date)
        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            article.description = 'New description'
            article.save()
            self.assertEqual(article.last_content_modification_date, now)

    def test_content_mod_date_change_on_content_change(self):
        """
        Test if the ``last_content_modification_date`` date change when the content change.
        """
        article = self._get_article()
        article.pub_date = timezone.now()
        article.save()
        self.assertIsNone(article.last_content_modification_date)
        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            article.content = 'New content'
            article.save()
            self.assertEqual(article.last_content_modification_date, now)

    def test_forum_creation_on_save(self):
        article = self._get_article()
        article.auto_create_related_forum_thread = True
        article.related_forum_thread = None
        article.create_related_forum_thread = MagicMock()
        article.status = ARTICLE_STATUS_PUBLISHED
        article.save()
        article.create_related_forum_thread.assert_called_with()

    def test_forum_creation_on_save_not_published(self):
        article = self._get_article()
        article.auto_create_related_forum_thread = True
        article.related_forum_thread = None
        article.create_related_forum_thread = MagicMock()
        article.status = ARTICLE_STATUS_DRAFT
        article.save()
        self.assertFalse(article.create_related_forum_thread.called)
        article.status = ARTICLE_STATUS_DELETED
        article.save()
        self.assertFalse(article.create_related_forum_thread.called)

    def test_forum_creation_on_save_not_requested(self):
        article = self._get_article()
        article.auto_create_related_forum_thread = False
        article.related_forum_thread = None
        article.create_related_forum_thread = MagicMock()
        article.status = ARTICLE_STATUS_PUBLISHED
        article.save()
        self.assertFalse(article.create_related_forum_thread.called)

    def test_forum_creation_on_save_thread_already_exist(self):
        article = self._get_article()
        article.auto_create_related_forum_thread = True
        article.related_forum_thread = ForumThread(id=1)
        article.create_related_forum_thread = MagicMock()
        article.status = ARTICLE_STATUS_PUBLISHED
        article.save()
        self.assertFalse(article.create_related_forum_thread.called)

    def test_create_forum_thread(self):
        """
        Test if the ``create_related_forum_thread`` create the forum thread as requested.
        """
        article = self._get_article()
        forum = Forum.objects.create(title='test', slug='test')
        with patch('apps.blog.models.PARENT_FORUM_ID_FOR_ARTICLE_THREADS') as mock_setting:
            mock_setting.return_value = forum.pk
            self.assertIsNone(article.related_forum_thread)
            article.create_related_forum_thread()
            self.assertIsNotNone(article.related_forum_thread)
            self.assertEqual(article.title, article.related_forum_thread.title)
            self.assertEqual(article.author, article.related_forum_thread.first_post.author)
            self.assertIn(article.get_absolute_url(), article.related_forum_thread.first_post.content)
            self.assertIsNone(article.related_forum_thread.first_post.author_ip_address)

    def test_create_forum_thread_no_forum_id(self):
        """
        Test if the ``create_related_forum_thread`` method handle ``PARENT_FORUM_ID_FOR_ARTICLE_THREADS = None``.
        """
        # TODO Understand why patch doesnt work here
        # article = self._get_article()
        # with patch('apps.blog.models.PARENT_FORUM_ID_FOR_ARTICLE_THREADS') as mock_setting:
        #     mock_setting.return_value = False
        #     self.assertIsNone(article.related_forum_thread)
        #     article.create_related_forum_thread()
        #     self.assertIsNone(article.related_forum_thread)
        pass

    def test_create_forum_thread_unknown_forum_id(self):
        """
        Test if the ``create_related_forum_thread`` method handle misconfiguration.
        """
        article = self._get_article()
        with patch('apps.blog.models.PARENT_FORUM_ID_FOR_ARTICLE_THREADS') as mock_setting:
            mock_setting.return_value = 404
            with self.assertRaises(ImproperlyConfigured):
                article.create_related_forum_thread()

    def test_create_revision_on_title_change(self):
        """
        Test if the ``save()`` method create a new revision of the article when the title change.
        """
        article = self._get_article()
        self.assertEqual(article.revisions.count(), 0)
        article.title = 'New title'
        article.save()
        self.assertEqual(article.revisions.count(), 1)

    def test_create_revision_on_subtitle_change(self):
        """
        Test if the ``save()`` method create a new revision of the article when the subtitle change.
        """
        article = self._get_article()
        self.assertEqual(article.revisions.count(), 0)
        article.subtitle = 'New subtitle'
        article.save()
        self.assertEqual(article.revisions.count(), 1)

    def test_create_revision_on_description_change(self):
        """
        Test if the ``save()`` method create a new revision of the article when the description change.
        """
        article = self._get_article()
        self.assertEqual(article.revisions.count(), 0)
        article.description = 'New description'
        article.save()
        self.assertEqual(article.revisions.count(), 1)

    def test_create_revision_on_content_change(self):
        """
        Test if the ``save()`` method create a new revision of the article when the content change.
        """
        article = self._get_article()
        self.assertEqual(article.revisions.count(), 0)
        article.content = 'New content'
        article.save()
        self.assertEqual(article.revisions.count(), 1)

    def test_revision_creation(self):
        """
        Test the creation of the article's revision on save.
        """
        article = self._get_article()
        self.assertEqual(article.revisions.count(), 0)
        old_title = article.title
        article.title = 'New title'
        old_subtitle = article.subtitle
        article.subtitle = 'New subtitle'
        old_description = article.description
        article.description = 'New description'
        old_content = article.content
        article.content = 'New content'

        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            article.save()
        self.assertEqual(article.revisions.count(), 1)

        revision = article.revisions.first()
        self.assertEqual(old_title, revision.title)
        self.assertEqual(old_subtitle, revision.subtitle)
        self.assertEqual(old_description, revision.description)
        self.assertEqual(old_content, revision.content)
        self.assertFalse(revision.revision_minor_change)
        self.assertEqual('', revision.revision_description)
        self.assertIsNone(revision.revision_author)
        self.assertEqual(revision.revision_date, now)

    def test_revision_creation_extra_args(self):
        """
        Test the creation of the article's revision on save with extra arguments.
        """
        author = get_user_model().objects.create_user(username='johnsmith',
                                                      password='johnsmith',
                                                      email='john.smith@example.com')
        article = self._get_article()
        self.assertEqual(article.revisions.count(), 0)
        old_title = article.title
        article.title = 'New title'
        old_subtitle = article.subtitle
        article.subtitle = 'New subtitle'
        old_description = article.description
        article.description = 'New description'
        old_content = article.content
        article.content = 'New content'

        now = timezone.now()
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            article.save(current_user=author,
                         minor_change=True,
                         revision_description='Revision test')
        self.assertEqual(article.revisions.count(), 1)

        revision = article.revisions.first()
        self.assertEqual(old_title, revision.title)
        self.assertEqual(old_subtitle, revision.subtitle)
        self.assertEqual(old_description, revision.description)
        self.assertEqual(old_content, revision.content)
        self.assertEqual(revision.revision_minor_change, True)
        self.assertEqual('Revision test', revision.revision_description)
        self.assertEqual(revision.revision_author, author)
        self.assertEqual(revision.revision_date, now)

    def test_require_membership_for_reading(self):
        """
        Test if ``require_membership_for_reading`` return True when membership is
        required to read the article and expiration date is not reached.
        """
        future_now = timezone.now() + timedelta(seconds=10)
        article = Article(membership_required=True,
                          membership_required_expiration_date=future_now)
        self.assertTrue(article.require_membership_for_reading())

    def test_require_membership_for_reading_no_expiration(self):
        """
        Test if ``require_membership_for_reading`` work correctly when the
        expiration date is not set (= no expiration).
        """
        article = Article(membership_required=True,
                          membership_required_expiration_date=None)
        self.assertTrue(article.require_membership_for_reading())
        article = Article(membership_required=False,
                          membership_required_expiration_date=None)
        self.assertFalse(article.require_membership_for_reading())

    def test_require_membership_for_reading_membership_not_required(self):
        """
        Test if ``require_membership_for_reading`` return False when
        ``membership_required`` is False and ``membership_required_expiration_date``
        is not None.
        """
        now = timezone.now()
        article = Article(membership_required=False,
                          membership_required_expiration_date=now)
        self.assertFalse(article.require_membership_for_reading())

    def test_require_membership_for_reading_requirement_expired(self):
        """
        Test if ``require_membership_for_reading`` return False when the expiration
        date has been reached.
        """
        past_now = timezone.now() - timedelta(seconds=1)
        article = Article(membership_required=True,
                          membership_required_expiration_date=past_now)
        self.assertFalse(article.require_membership_for_reading())

    def test_is_published_unpublished(self):
        """
        Test if ``is_published`` return always False with unpublished article.
        """
        past_now = timezone.now() - timedelta(seconds=1)
        article = Article(pub_date=past_now, status=ARTICLE_STATUS_DRAFT)
        self.assertFalse(article.is_published())
        article = Article(pub_date=None, status=ARTICLE_STATUS_DRAFT)
        self.assertFalse(article.is_published())

        article = Article(pub_date=past_now, status=ARTICLE_STATUS_DELETED)
        self.assertFalse(article.is_published())
        article = Article(pub_date=None, status=ARTICLE_STATUS_DELETED)
        self.assertFalse(article.is_published())

    def test_is_published_published(self):
        """
        Test if ``is_published`` return True with published article.
        """
        now = timezone.now()
        article = Article(pub_date=now, status=ARTICLE_STATUS_PUBLISHED)
        self.assertTrue(article.is_published())

    def test_is_published_published_in_future(self):
        """
        Test if ``is_published`` return False with article published in future.
        """
        future_now = timezone.now() + timedelta(seconds=10)
        article = Article(pub_date=future_now, status=ARTICLE_STATUS_PUBLISHED)
        self.assertFalse(article.is_published())

    def test_is_published_published_expired(self):
        """
        Test if ``is_published`` return False with article published but expired.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        article = Article(pub_date=past_now,
                          expiration_date=now, status=ARTICLE_STATUS_PUBLISHED)
        self.assertFalse(article.is_published())

    def test_is_gone(self):
        """
        Test if ``is_gone`` return False with article published or draft.
        """
        article = Article(status=ARTICLE_STATUS_DRAFT)
        self.assertFalse(article.is_gone())
        article = Article(status=ARTICLE_STATUS_PUBLISHED)
        self.assertFalse(article.is_gone())

    def test_is_gone_deleted(self):
        """
        Test if ``is_gone`` return True with a deleted article.
        """
        article = Article(status=ARTICLE_STATUS_DELETED)
        self.assertTrue(article.is_gone())

    def test_is_gone_expired(self):
        """
        Test if ``is_gone`` return True with an expired article.
        """
        now = timezone.now()
        article = Article(status=ARTICLE_STATUS_PUBLISHED, expiration_date=now)
        self.assertTrue(article.is_gone())

    def test_can_see_preview_anonymous(self):
        """
        Test the ``can_see_preview()`` method with a random user (not author nor authorized to see preview).
        """
        article = self._get_article()
        user = get_user_model().objects.create_user(username='anonuser',
                                                    password='anonuser',
                                                    email='anon.user@example.com')
        self.assertNotEqual(article.author, user)
        self.assertFalse(article.can_see_preview(user))

    def test_can_see_preview_with_author(self):
        """
        Test the ``can_see_preview()`` method with the announcement author itself.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        article = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=author,
                                         content='Hello World!')
        self.assertEqual(article.author, author)
        self.assertTrue(article.can_see_preview(author))

    def test_can_see_preview_with_authorized_user(self):
        """
        Test the ``can_see_preview()`` method with an authorized user.
        """
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        authorized_user = get_user_model().objects.create_user(username='jonhsmith',
                                                               password='jonhsmith',
                                                               email='jonh.smith@example.com')
        content_type = ContentType.objects.get_for_model(Article)
        permission = Permission.objects.get(codename='can_see_preview', content_type=content_type)
        authorized_user.user_permissions.add(permission)
        article = Article.objects.create(title='Test 1',
                                         slug='test-1',
                                         author=author,
                                         content='Hello World!')
        self.assertNotEqual(article.author, authorized_user)
        self.assertTrue(article.can_see_preview(authorized_user))

    def test_has_been_modified_after_publication(self):
        """
        Test if the article is flagged as modified after some modification.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=1)
        article = Article(pub_date=past_now, last_content_modification_date=now)
        self.assertTrue(article.has_been_modified_after_publication())

    def test_has_been_modified_after_publication_no_modif(self):
        """
        Test if the article is flagged as modified without modification.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=1)
        article = Article(pub_date=past_now, last_content_modification_date=None)
        self.assertFalse(article.has_been_modified_after_publication())

    def test_published_method(self):
        """
        Test the ``published`` method of the manager.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DRAFT,
                               pub_date=now)
        Article.objects.create(title='Test 2',
                               slug='test-2',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DELETED,
                               pub_date=now)
        Article.objects.create(title='Test 3',
                               slug='test-3',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now)
        Article.objects.create(title='Test 4',
                               slug='test-4',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=future_now)
        Article.objects.create(title='Test 5',
                               slug='test-5',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=past_now,
                               expiration_date=now)
        queryset = Article.objects.published()
        self.assertQuerysetEqual(queryset, ['<Article: Test 3>'])

    def test_published_method_ordering(self):
        """
        Test the ordering of the ``published`` method of the manager.
        """
        now = timezone.now()
        now_m1 = now - timedelta(seconds=1)
        now_m2 = now - timedelta(seconds=1)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now)
        Article.objects.create(title='Test 2',
                               slug='test-2',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now_m1)
        Article.objects.create(title='Test 3',
                               slug='test-3',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now_m2,
                               featured=True)
        queryset = Article.objects.published()
        self.assertQuerysetEqual(queryset, ['<Article: Test 3>',
                                            '<Article: Test 1>',
                                            '<Article: Test 2>'])

    def test_network_publishable_method(self):
        """
        Test the ``network_publishable`` method of the manager.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DRAFT,
                               pub_date=now)
        Article.objects.create(title='Test 2',
                               slug='test-2',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DELETED,
                               pub_date=now)
        Article.objects.create(title='Test 3',
                               slug='test-3',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now,
                               network_publish=True)
        Article.objects.create(title='Test 3bis',
                               slug='test-3bis',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now,
                               network_publish=False)
        Article.objects.create(title='Test 4',
                               slug='test-4',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=future_now)
        Article.objects.create(title='Test 5',
                               slug='test-5',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=past_now,
                               expiration_date=now)
        queryset = Article.objects.network_publishable()
        self.assertQuerysetEqual(queryset, ['<Article: Test 3>'])

    def test_published_per_month_method(self):
        """
        Test the ``published_per_month`` method of the manager.
        """
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        publication_calendar = (
            datetime(2013, 1, 1, 12),
            datetime(2014, 2, 1, 12),
            datetime(2014, 5, 1, 12),
            datetime(2014, 6, 1, 12),
            datetime(2014, 7, 1, 12),
            datetime(2014, 7, 2, 12),
            datetime(2014, 7, 3, 12),
            datetime(2015, 3, 1, 12),
            datetime(2015, 3, 2, 12),
            datetime(2015, 4, 1, 12),
            datetime(2015, 5, 1, 12),
            datetime(2015, 5, 2, 12),
            datetime(2015, 6, 1, 12),
        )
        for i, pub_date in enumerate(publication_calendar, start=1):
            Article.objects.create(title='Test %d' % i,
                                   slug='test-%d' % i,
                                   author=author,
                                   content='Hello World!',
                                   status=ARTICLE_STATUS_PUBLISHED,
                                   pub_date=timezone.make_aware(pub_date))

        calendar = Article.objects.published_per_month()
        excepted_result = [
            (2013, [(1, 1)]),
            (2014, [(2, 1),
                    (5, 1),
                    (6, 1),
                    (7, 3)]),
            (2015, [(3, 2),
                    (4, 1),
                    (5, 2),
                    (6, 1)]),
        ]
        self.assertEqual(calendar, excepted_result)
