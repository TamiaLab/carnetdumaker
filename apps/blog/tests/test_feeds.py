"""
Tests suite for the feeds of the blog app.
"""

from datetime import timedelta, datetime
from unittest.mock import MagicMock

from django.test import SimpleTestCase, TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.test.utils import override_settings

from apps.licenses.models import License

from ..models import (Article,
                      ArticleTag,
                      ArticleCategory)
from ..constants import (ARTICLE_STATUS_DRAFT,
                         ARTICLE_STATUS_PUBLISHED,
                         ARTICLE_STATUS_DELETED)
from ..settings import NB_ARTICLES_PER_FEED
from ..feeds import (BaseBlogArticleFeed,
                     LatestArticlesFeed,
                     LatestArticlesAtomFeed,
                     LatestArticlesForCategoryFeed,
                     LatestArticlesForCategoryAtomFeed,
                     LatestArticlesForLicenseFeed,
                     LatestArticlesForLicenseAtomFeed,
                     LatestArticlesForTagFeed,
                     LatestArticlesForTagAtomFeed,
                     ArticlesForYearFeed,
                     ArticlesForYearAtomFeed,
                     ArticlesForYearAndMonthFeed,
                     ArticlesForYearAndMonthAtomFeed)


class BaseBlogArticleFeedTestCase(SimpleTestCase):
    """
    Tests suite for the ``BaseBlogArticleFeed`` base feed class.
    """

    def test_items(self):
        """
        Test the base ``items`` method. Should raise ``NotImplementedError``.
        """
        feed = BaseBlogArticleFeed()
        with self.assertRaises(NotImplementedError):
            feed.items()

    def test_item_title(self):
        """
        Test the base ``item_title`` method.
        """
        item = MagicMock(title='Test')
        feed = BaseBlogArticleFeed()
        self.assertEqual(item.title, feed.item_title(item))

    def test_item_description_with_content(self):
        """
        Test the base ``item_description`` method with some content text but no description.
        """
        item = MagicMock(content_html='Test', description_html='')
        feed = BaseBlogArticleFeed()
        self.assertEqual(item.content_html, feed.item_description(item))

    def test_item_description_with_description(self):
        """
        Test the base ``item_description`` method with a description.
        """
        item = MagicMock(content_html='Test', description_html='Description')
        feed = BaseBlogArticleFeed()
        self.assertEqual('<p><strong>%s</strong></p>\n%s' % (item.description_html, item.content_html),
                         feed.item_description(item))

    def test_item_author_name(self):
        """
        Test the base ``item_author_name`` method.
        """
        item = MagicMock()
        item.author = MagicMock(username='Johndoe', is_active=True)
        feed = BaseBlogArticleFeed()
        self.assertEqual(item.author.username, feed.item_author_name(item))

    def test_item_author_name_anonymous(self):
        """
        Test the base ``item_author_name`` method with an inactive user.
        """
        item = MagicMock()
        item.author = MagicMock(username='Johndoe', is_active=False)
        feed = BaseBlogArticleFeed()
        self.assertEqual(_('Anonymous'), feed.item_author_name(item))

    def test_item_pubdate(self):
        """
        Test the base ``item_pubdate`` method.
        """
        item = MagicMock(pub_date=timezone.now())
        feed = BaseBlogArticleFeed()
        self.assertEqual(item.pub_date, feed.item_pubdate(item))

    def test_item_updateddate(self):
        """
        Test the base ``item_updateddate`` method.
        """
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        item = MagicMock(last_content_modification_date=now, pub_date=past_now)
        feed = BaseBlogArticleFeed()
        self.assertEqual(item.last_content_modification_date, feed.item_updateddate(item))

    def test_item_updateddate_no_mod_date(self):
        """
        Test the base ``item_updateddate`` method without modification date.
        """
        now = timezone.now()
        item = MagicMock(last_content_modification_date=None, pub_date=now)
        feed = BaseBlogArticleFeed()
        self.assertEqual(item.pub_date, feed.item_updateddate(item))

    def test_item_categories(self):
        """
        Test the base ``item_categories`` method.
        """
        from collections import namedtuple
        item = MagicMock()
        mock_cat = namedtuple('ArticleCategory', ['name'])
        item.categories.all.return_value = [mock_cat(name='cat1'),
                                            mock_cat(name='cat2'),
                                            mock_cat(name='cat3'),
                                            mock_cat(name='cat4')]
        mock_tag = namedtuple('ArticleTag', ['name'])
        item.tags.all.return_value = [mock_tag(name='tag1'),
                                      mock_tag(name='tag2'),
                                      mock_tag(name='tag3'),
                                      mock_tag(name='tag4')]
        feed = BaseBlogArticleFeed()
        self.assertEqual(feed.item_categories(item), ['cat1', 'cat2', 'cat3', 'cat4',
                                                      'tag1', 'tag2', 'tag3', 'tag4'])


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LatestArticlesFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestArticlesFeed`` feed class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestArticlesFeed()
        self.assertEqual(feed.title, _('Latest articles'))
        self.assertEqual(feed.link, reverse('blog:index'))
        self.assertEqual(feed.feed_url, reverse('blog:latest_articles_rss'))
        self.assertEqual(feed.description, _('Latest articles, all categories together'))

    def test_feed_items(self):
        """
        Test the items returned by the ``items`` method of the feed.
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
        feed = LatestArticlesFeed()
        queryset = feed.items()
        self.assertQuerysetEqual(queryset, ['<Article: Test 3>'])

    def test_items_limit(self):
        """
        Test if only the N most recent articles are included in the feed.
        """
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        articles = []
        for i in range(NB_ARTICLES_PER_FEED + 5):
            pub_date = now - timedelta(seconds=i)
            obj = Article.objects.create(title='Test %d' % i,
                               slug='test-%d' % i,
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=pub_date)
            articles.append(repr(obj))

        # Test the object in the feed
        feed = LatestArticlesFeed()
        items = feed.items()
        self.assertQuerysetEqual(items, articles[:NB_ARTICLES_PER_FEED])


class LatestArticlesAtomFeedTestCase(SimpleTestCase):
    """
    Tests suite for the ``LatestArticlesAtomFeed`` feed class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        feed = LatestArticlesAtomFeed()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.title, LatestArticlesFeed.title)
        self.assertEqual(feed.link, LatestArticlesFeed.link)
        self.assertEqual(feed.feed_url, reverse('blog:latest_articles_atom'))
        self.assertEqual(feed.subtitle, LatestArticlesFeed.description)


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LatestArticlesForCategoryFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestArticlesForCategoryFeed`` class.
    """

    def test_feed_get_object(self):
        """
        Test the ``get_object`` method of the feed.
        """

        # Create some test fixtures
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForCategoryFeed()
        self.assertEqual(feed.get_object(None, hierarchy='test-1'), category)

    def test_feed_title(self):
        """
        Test the ``title`` method of the feed.
        """

        # Create some test fixtures
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForCategoryFeed()
        self.assertEqual(feed.title(category), _('Latest articles in category "%s"') % category.name)

    def test_feed_link(self):
        """
        Test the ``link`` method of the feed.
        """

        # Create some test fixtures
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForCategoryFeed()
        self.assertEqual(feed.link(category), category.get_absolute_url())

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForCategoryFeed()
        self.assertEqual(feed.feed_url(category), category.get_latest_articles_rss_feed_url())

    def test_feed_description(self):
        """
        Test the ``description`` method of the feed.
        """

        # Create some test fixtures
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1', description='Test')

        # Test the method
        feed = LatestArticlesForCategoryFeed()
        self.assertEqual(feed.description(category), category.description_html)

    def test_feed_description_no_description(self):
        """
        Test the ``description`` method of the feed with no description.
        """

        # Create some test fixtures
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForCategoryFeed()
        self.assertEqual(feed.description(category), _('Latest articles in category "%s"') % category.name)

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DRAFT,
                               pub_date=now).categories.add(category)
        Article.objects.create(title='Test 2',
                               slug='test-2',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DELETED,
                               pub_date=now).categories.add(category)
        Article.objects.create(title='Test 3',
                               slug='test-3',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now).categories.add(category)
        Article.objects.create(title='Test 4',
                               slug='test-4',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=future_now).categories.add(category)
        Article.objects.create(title='Test 5',
                               slug='test-5',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=past_now,
                               expiration_date=now).categories.add(category)

        # Test the resulting feed content
        feed = LatestArticlesForCategoryFeed()
        items = feed.items(category)
        self.assertQuerysetEqual(items, ['<Article: Test 3>'])

    def test_items_limit(self):
        """
        Test if only the N most recent announcements are included in the feed.
        """
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')
        articles = []
        for i in range(NB_ARTICLES_PER_FEED + 5):
            pub_date = now - timedelta(seconds=i)
            obj = Article.objects.create(title='Test %d' % i,
                               slug='test-%d' % i,
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=pub_date)
            obj.categories.add(category)
            articles.append(repr(obj))

        # Test the object in the feed
        feed = LatestArticlesForCategoryFeed()
        items = feed.items(category)
        self.assertQuerysetEqual(items, articles[:NB_ARTICLES_PER_FEED])


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LatestArticlesForCategoryAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestArticlesForCategoryAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        self.assertEqual(LatestArticlesForCategoryAtomFeed.feed_type, Atom1Feed)
        self.assertEqual(LatestArticlesForCategoryAtomFeed.title, LatestArticlesForCategoryFeed.title)
        self.assertEqual(LatestArticlesForCategoryAtomFeed.link, LatestArticlesForCategoryFeed.link)
        self.assertEqual(LatestArticlesForCategoryAtomFeed.subtitle, LatestArticlesForCategoryFeed.description)

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        category = ArticleCategory.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForCategoryAtomFeed()
        self.assertEqual(feed.feed_url(category), category.get_latest_articles_atom_feed_url())

@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LatestArticlesForLicenseFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestArticlesForLicenseFeed`` class.
    """

    def test_feed_get_object(self):
        """
        Test the ``get_object`` method of the feed.
        """

        # Create some test fixtures
        license = License.objects.create(name='License 1', slug='license-1')

        # Test the method
        feed = LatestArticlesForLicenseFeed()
        self.assertEqual(feed.get_object(None, slug='license-1'), license)

    def test_feed_title(self):
        """
        Test the ``title`` method of the feed.
        """

        # Create some test fixtures
        license = License.objects.create(name='License 1', slug='license-1')

        # Test the method
        feed = LatestArticlesForLicenseFeed()
        self.assertEqual(feed.title(license), _('Latest articles with license "%s"') % license.name)

    def test_feed_link(self):
        """
        Test the ``link`` method of the feed.
        """

        # Create some test fixtures
        license = License.objects.create(name='License 1', slug='license-1')

        # Test the method
        feed = LatestArticlesForLicenseFeed()
        self.assertEqual(feed.link(license), reverse('bloglicense:license_articles_detail', kwargs={'slug': license.slug}))

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        license = License.objects.create(name='License 1', slug='license-1')

        # Test the method
        feed = LatestArticlesForLicenseFeed()
        self.assertEqual(feed.feed_url(license), reverse('bloglicense:latest_license_articles_rss',
                                                         kwargs={'slug': license.slug}))

    def test_feed_description(self):
        """
        Test the ``description`` method of the feed.
        """

        # Create some test fixtures
        license = License.objects.create(name='License 1', slug='license-1', description='Test')

        # Test the method
        feed = LatestArticlesForLicenseFeed()
        self.assertEqual(feed.description(license), license.description_html)

    def test_feed_description_no_description(self):
        """
        Test the ``description`` method of the feed with no description.
        """

        # Create some test fixtures
        license = License.objects.create(name='License 1', slug='license-1')

        # Test the method
        feed = LatestArticlesForLicenseFeed()
        self.assertEqual(feed.description(license), _('Latest articles with license "%s"') % license.name)

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        license = License.objects.create(name='License 1', slug='license-1')
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DRAFT,
                               pub_date=now,
                               license=license)
        Article.objects.create(title='Test 2',
                               slug='test-2',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DELETED,
                               pub_date=now,
                               license=license)
        Article.objects.create(title='Test 3',
                               slug='test-3',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now,
                               license=license)
        Article.objects.create(title='Test 4',
                               slug='test-4',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=future_now,
                               license=license)
        Article.objects.create(title='Test 5',
                               slug='test-5',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=past_now,
                               expiration_date=now,
                               license=license)

        # Test the resulting feed content
        feed = LatestArticlesForLicenseFeed()
        items = feed.items(license)
        self.assertQuerysetEqual(items, ['<Article: Test 3>'])

    def test_items_limit(self):
        """
        Test if only the N most recent announcements are included in the feed.
        """
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        license = License.objects.create(name='License 1', slug='license-1')
        articles = []
        for i in range(NB_ARTICLES_PER_FEED + 5):
            pub_date = now - timedelta(seconds=i)
            obj = Article.objects.create(title='Test %d' % i,
                               slug='test-%d' % i,
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=pub_date,
                               license=license)
            articles.append(repr(obj))

        # Test the object in the feed
        feed = LatestArticlesForLicenseFeed()
        items = feed.items(license)
        self.assertQuerysetEqual(items, articles[:NB_ARTICLES_PER_FEED])


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LatestArticlesForLicenseAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestArticlesForLicenseAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        self.assertEqual(LatestArticlesForLicenseAtomFeed.feed_type, Atom1Feed)
        self.assertEqual(LatestArticlesForLicenseAtomFeed.title, LatestArticlesForLicenseFeed.title)
        self.assertEqual(LatestArticlesForLicenseAtomFeed.link, LatestArticlesForLicenseFeed.link)
        self.assertEqual(LatestArticlesForLicenseAtomFeed.subtitle, LatestArticlesForLicenseFeed.description)

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        license = License.objects.create(name='License 1', slug='license-1')

        # Test the method
        feed = LatestArticlesForLicenseAtomFeed()
        self.assertEqual(feed.feed_url(license), reverse('bloglicense:latest_license_articles_atom',
                                                         kwargs={'slug': license.slug}))


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LatestArticlesForTagFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestArticlesForTagFeed`` class.
    """

    def test_feed_get_object(self):
        """
        Test the ``get_object`` method of the feed.
        """

        # Create some test fixtures
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForTagFeed()
        self.assertEqual(feed.get_object(None, slug='test-1'), tag)

    def test_feed_title(self):
        """
        Test the ``title`` method of the feed.
        """

        # Create some test fixtures
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForTagFeed()
        self.assertEqual(feed.title(tag), _('Latest articles with tag "%s"') % tag.name)

    def test_feed_link(self):
        """
        Test the ``link`` method of the feed.
        """

        # Create some test fixtures
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForTagFeed()
        self.assertEqual(feed.link(tag), tag.get_absolute_url())

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForTagFeed()
        self.assertEqual(feed.feed_url(tag), tag.get_latest_articles_rss_feed_url())

    def test_feed_description(self):
        """
        Test the ``description`` method of the feed.
        """

        # Create some test fixtures
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForTagFeed()
        self.assertEqual(feed.description(tag), _('Latest articles with tag "%s"') % tag.name)

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
        now = timezone.now()
        past_now = now - timedelta(seconds=10)
        future_now = now + timedelta(seconds=10)
        author = get_user_model().objects.create_user(username='johndoe',
                                                      password='johndoe',
                                                      email='john.doe@example.com')
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')
        Article.objects.create(title='Test 1',
                               slug='test-1',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DRAFT,
                               pub_date=now).tags.add(tag)
        Article.objects.create(title='Test 2',
                               slug='test-2',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_DELETED,
                               pub_date=now).tags.add(tag)
        Article.objects.create(title='Test 3',
                               slug='test-3',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=now).tags.add(tag)
        Article.objects.create(title='Test 4',
                               slug='test-4',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=future_now).tags.add(tag)
        Article.objects.create(title='Test 5',
                               slug='test-5',
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=past_now,
                               expiration_date=now).tags.add(tag)

        # Test the resulting feed content
        feed = LatestArticlesForTagFeed()
        items = feed.items(tag)
        self.assertQuerysetEqual(items, ['<Article: Test 3>'])

    def test_items_limit(self):
        """
        Test if only the N most recent announcements are included in the feed.
        """
        now = timezone.now()
        author = get_user_model().objects.create_user(username='jonhdoe',
                                                      password='jonhdoe',
                                                      email='jonh.doe@example.com')
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')
        articles = []
        for i in range(NB_ARTICLES_PER_FEED + 5):
            pub_date = now - timedelta(seconds=i)
            obj = Article.objects.create(title='Test %d' % i,
                               slug='test-%d' % i,
                               author=author,
                               content='Hello World!',
                               status=ARTICLE_STATUS_PUBLISHED,
                               pub_date=pub_date)
            obj.tags.add(tag)
            articles.append(repr(obj))

        # Test the object in the feed
        feed = LatestArticlesForTagFeed()
        items = feed.items(tag)
        self.assertQuerysetEqual(items, articles[:NB_ARTICLES_PER_FEED])


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class LatestArticlesForTagAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``LatestArticlesForTagAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        self.assertEqual(LatestArticlesForTagAtomFeed.feed_type, Atom1Feed)
        self.assertEqual(LatestArticlesForTagAtomFeed.title, LatestArticlesForTagFeed.title)
        self.assertEqual(LatestArticlesForTagAtomFeed.link, LatestArticlesForTagFeed.link)
        self.assertEqual(LatestArticlesForTagAtomFeed.subtitle, LatestArticlesForTagFeed.description)

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        tag = ArticleTag.objects.create(name='Test 1', slug='test-1')

        # Test the method
        feed = LatestArticlesForTagAtomFeed()
        self.assertEqual(feed.feed_url(tag), tag.get_latest_articles_atom_feed_url())


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticlesForYearFeedTestCase(TestCase):
    """
    Tests suite for the ``ArticlesForYearFeed`` class.
    """

    def test_feed_get_object(self):
        """
        Test the ``get_object`` method of the feed.
        """

        # Test the method
        feed = ArticlesForYearFeed()
        self.assertEqual(feed.get_object(None, year='2015'), {'year': '2015'})

    def test_feed_title(self):
        """
        Test the ``title`` method of the feed.
        """

        # Create some test fixtures
        year = {'year': '2015'}

        # Test the method
        feed = ArticlesForYearFeed()
        self.assertEqual(feed.title(year), _('Latest articles for year %(year)s') % year)

    def test_feed_link(self):
        """
        Test the ``link`` method of the feed.
        """

        # Create some test fixtures
        year = {'year': '2015'}

        # Test the method
        feed = ArticlesForYearFeed()
        self.assertEqual(feed.link(year), reverse('blog:archive_year', kwargs=year))

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        year = {'year': '2015'}

        # Test the method
        feed = ArticlesForYearFeed()
        self.assertEqual(feed.feed_url(year), reverse('blog:articles_archive_year_rss', kwargs=year))

    def test_feed_description(self):
        """
        Test the ``description`` method of the feed.
        """

        # Create some test fixtures
        year = {'year': '2015'}

        # Test the method
        feed = ArticlesForYearFeed()
        self.assertEqual(feed.description(year), _('Latest articles for year %(year)s') % year)

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
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

        # Test the resulting feed content
        feed = ArticlesForYearFeed()
        items = feed.items({'year': '2014'})
        self.assertQuerysetEqual(items, ['<Article: Test 7>',
                                         '<Article: Test 6>',
                                         '<Article: Test 5>',
                                         '<Article: Test 4>',
                                         '<Article: Test 3>',
                                         '<Article: Test 2>'])


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticlesForYearAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``ArticlesForYearAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        self.assertEqual(ArticlesForYearAtomFeed.feed_type, Atom1Feed)
        self.assertEqual(ArticlesForYearAtomFeed.title, ArticlesForYearFeed.title)
        self.assertEqual(ArticlesForYearAtomFeed.link, ArticlesForYearFeed.link)
        self.assertEqual(ArticlesForYearAtomFeed.subtitle, ArticlesForYearFeed.description)

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        year = {'year': '2015'}

        # Test the method
        feed = ArticlesForYearAtomFeed()
        self.assertEqual(feed.feed_url(year), reverse('blog:articles_archive_year_atom', kwargs=year))


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticlesForYearAndMonthFeedTestCase(TestCase):
    """
    Tests suite for the ``ArticlesForYearAndMonthFeed`` class.
    """

    def test_feed_get_object(self):
        """
        Test the ``get_object`` method of the feed.
        """

        # Test the method
        feed = ArticlesForYearAndMonthFeed()
        self.assertEqual(feed.get_object(None, year='2015', month='02'), {'year': '2015', 'month': '02'})

    def test_feed_title(self):
        """
        Test the ``title`` method of the feed.
        """

        # Create some test fixtures
        year_month = {'year': '2015', 'month': '02'}

        # Test the method
        feed = ArticlesForYearAndMonthFeed()
        self.assertEqual(feed.title(year_month), _('Latest articles for month %(year)s/%(month)s') % year_month)

    def test_feed_link(self):
        """
        Test the ``link`` method of the feed.
        """

        # Create some test fixtures
        year_month = {'year': '2015', 'month': '02'}

        # Test the method
        feed = ArticlesForYearAndMonthFeed()
        self.assertEqual(feed.link(year_month), reverse('blog:archive_month', kwargs=year_month))

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        year_month = {'year': '2015', 'month': '02'}

        # Test the method
        feed = ArticlesForYearAndMonthFeed()
        self.assertEqual(feed.feed_url(year_month), reverse('blog:articles_archive_month_rss', kwargs=year_month))

    def test_feed_description(self):
        """
        Test the ``description`` method of the feed.
        """

        # Create some test fixtures
        year_month = {'year': '2015', 'month': '02'}

        # Test the method
        feed = ArticlesForYearAndMonthFeed()
        self.assertEqual(feed.description(year_month), _('Latest articles for month %(year)s/%(month)s') % year_month)

    def test_feed_items(self):
        """
        Test the ``items`` method of the feed.
        """

        # Create some test fixtures
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

        # Test the resulting feed content
        feed = ArticlesForYearAndMonthFeed()
        items = feed.items({'year': '2014', 'month': '07'})
        self.assertQuerysetEqual(items, ['<Article: Test 7>',
                                         '<Article: Test 6>',
                                         '<Article: Test 5>'])


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ArticlesForYearAndMonthAtomFeedTestCase(TestCase):
    """
    Tests suite for the ``ArticlesForYearAndMonthAtomFeed`` class.
    """

    def test_feed_meta(self):
        """
        Test if the metadata of the feed are OK.
        """
        self.assertEqual(ArticlesForYearAndMonthAtomFeed.feed_type, Atom1Feed)
        self.assertEqual(ArticlesForYearAndMonthAtomFeed.title, ArticlesForYearAndMonthFeed.title)
        self.assertEqual(ArticlesForYearAndMonthAtomFeed.link, ArticlesForYearAndMonthFeed.link)
        self.assertEqual(ArticlesForYearAndMonthAtomFeed.subtitle, ArticlesForYearAndMonthFeed.description)

    def test_feed_url(self):
        """
        Test the ``feed_url`` method of the feed.
        """

        # Create some test fixtures
        year_month = {'year': '2015', 'month': '02'}

        # Test the method
        feed = ArticlesForYearAndMonthAtomFeed()
        self.assertEqual(feed.feed_url(year_month), reverse('blog:articles_archive_month_atom', kwargs=year_month))
