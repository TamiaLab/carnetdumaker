"""
Tests suite for the models of the image attachments app.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import ImageAttachment


class ImageAttachmentTestCase(TestCase):
    """
    Tests case for the ``ImageAttachment`` data model.
    """

    def _get_image(self):
        """
        Create a new image attachment.
        :return: The newly created image attachment.
        """
        image = ImageAttachment.objects.create(title='Test 1',
                                               slug='test-1',
                                               img_original='fixtures/beautifulfrog.jpg')
        return image

    def test_default_values(self):
        """
        Test default values of newly created image attachment.
        """
        image = self._get_image()
        self.assertIsNotNone(image.pub_date)
        self.assertEqual('', image.legend)
        self.assertEqual('', image.description)
        self.assertIsNone(image.license)
        self.assertIsNotNone('', image.img_original)
        self.assertTrue(image.img_original_height > 0)
        self.assertTrue(image.img_original_width > 0)
        self.assertIsNotNone('', image.img_small)
        self.assertTrue(image.img_small_height > 0)
        self.assertTrue(image.img_small_width > 0)
        self.assertIsNotNone('', image.img_medium)
        self.assertTrue(image.img_medium_height > 0)
        self.assertTrue(image.img_medium_width > 0)
        self.assertIsNotNone('', image.img_large)
        self.assertTrue(image.img_large_height > 0)
        self.assertTrue(image.img_large_width > 0)

    def test_str_method(self):
        """
        Test __str__ result for other tests.
        """
        image = self._get_image()
        self.assertEqual(image.title, str(image))

    def test_get_absolute_url_method(self):
        """
        Test get_absolute_url method with a valid image attachment.
        """
        image = self._get_image()
        excepted_url = reverse('imageattachments:image_attachment_detail', kwargs={'slug': image.slug})
        self.assertEqual(excepted_url, image.get_absolute_url())

    def test_ordering(self):
        """
        Test the ordering of image attachment object.
        """
        ImageAttachment.objects.create(title='Test 1',
                                       slug='test-1',
                                       img_original='fixtures/beautifulfrog.jpg')
        ImageAttachment.objects.create(title='Test 2',
                                       slug='test-2',
                                       img_original='fixtures/beautifulfrog.jpg')
        ImageAttachment.objects.create(title='Test 3',
                                       slug='test-3',
                                       img_original='fixtures/beautifulfrog.jpg')
        queryset = ImageAttachment.objects.all()
        self.assertQuerysetEqual(queryset, ['<ImageAttachment: Test 3>',
                                            '<ImageAttachment: Test 2>',
                                            '<ImageAttachment: Test 1>'])

    def test_save_model_with_no_new_upload(self):
        """
        Check if saving the model without uploading a new image change the image.
        """
        image = self._get_image()
        prev_img_original_url = image.img_original.url
        prev_img_small_url = image.img_small.url
        prev_img_medium_url = image.img_medium.url
        prev_img_large_url = image.img_large.url
        image.save()
        self.assertEqual(prev_img_original_url, image.img_original.url)
        self.assertEqual(prev_img_small_url, image.img_small.url)
        self.assertEqual(prev_img_medium_url, image.img_medium.url)
        self.assertEqual(prev_img_large_url, image.img_large.url)

    def test_save_model_with_no_thumbnails(self):
        """
        Check if saving a model without thumbnails generated them.
        """
        image = self._get_image()
        self.assertIsNotNone(image.img_original)
        image.img_small = None
        self.assertIsNone(image.img_small.name)
        image.img_medium = None
        self.assertIsNone(image.img_medium.name)
        image.img_large = None
        self.assertIsNone(image.img_large.name)
        image.save()
        self.assertIsNotNone(image.img_original.name)
        self.assertIsNotNone(image.img_small.name)
        self.assertIsNotNone(image.img_medium.name)
        self.assertIsNotNone(image.img_large.name)

    def test_save_model_with_new_upload(self):
        """
        Check if saving the model with a new image uploaded change the image and thumbnails.
        """
        image = self._get_image()
        prev_img_original_url = image.img_original.url
        prev_img_small_url = image.img_small.url
        prev_img_medium_url = image.img_medium.url
        prev_img_large_url = image.img_large.url
        with open('./uploads/fixtures/mea.jpg', 'rb') as f:
            content = f.read()
        new_image = SimpleUploadedFile(name='mea.jpg', content=content, content_type='image/jpeg')
        image.img_original = new_image
        image.save()
        self.assertNotEqual(prev_img_original_url, image.img_original.url)
        self.assertNotEqual(prev_img_small_url, image.img_small.url)
        self.assertNotEqual(prev_img_medium_url, image.img_medium.url)
        self.assertNotEqual(prev_img_large_url, image.img_large.url)

    def test_published_future(self):
        """
        Test the ``published`` method of the manager.
        """

        # Create some fixtures, one published and one in future
        future_now = timezone.now() + timedelta(seconds=10)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = future_now
            ImageAttachment.objects.create(title='Test 1',
                                           slug='test-1',
                                           img_original='fixtures/mea.jpg')
        ImageAttachment.objects.create(title='Test 2',
                                       slug='test-2',
                                       img_original='fixtures/mea.jpg')

        # Test the result
        queryset = ImageAttachment.objects.published()
        self.assertQuerysetEqual(queryset, ['<ImageAttachment: Test 2>'])
