"""
Test suite for the views of the image attachments app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings

from ..models import ImageAttachment


@override_settings(MEDIA_ROOT=settings.DEBUG_MEDIA_ROOT)
class ImageAttachmentViewsTestCase(TestCase):
    """
    Test suite for the views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.image1 = ImageAttachment.objects.create(title='Test 1',
                                                     slug='test-1',
                                                     description='Image 1',
                                                     img_original='fixtures/mea.jpg')
        self.image2 = ImageAttachment.objects.create(title='Test 2',
                                                     slug='test-2',
                                                     description='Image 2',
                                                     img_original='fixtures/mea.jpg',
                                                     public_listing=False)
        self.image3 = ImageAttachment.objects.create(title='Test 3',
                                                     slug='test-3',
                                                     description='Image 3',
                                                     img_original='fixtures/mea.jpg')

    def test_images_list_view_available(self):
        """
        Test the availability of the "images list" view.
        """
        client = Client()
        response = client.get(reverse('imageattachments:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'imageattachments/image_attachment_list.html')
        self.assertIn('images', response.context)
        self.assertQuerysetEqual(response.context['images'], ['<ImageAttachment: Test 3>',
                                                              '<ImageAttachment: Test 1>'])

    def test_image_detail_view_available(self):
        """
        Test the availability of the "image detail" view.
        """
        client = Client()
        response = client.get(self.image1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'imageattachments/image_attachment_detail.html')
        self.assertIn('image', response.context)
        self.assertEqual(response.context['image'], self.image1)

    def test_image_detail_view_available_with_no_public_listing(self):
        """
        Test the availability of the "image detail" view when the image is not publicity listed.
        """
        client = Client()
        response = client.get(self.image2.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'imageattachments/image_attachment_detail.html')
        self.assertIn('image', response.context)
        self.assertEqual(response.context['image'], self.image2)

    def test_image_detail_view_unavailable_with_unknown_slug(self):
        """
        Test the unavailability of the "image detail" view with an unknown image's slug.
        """
        client = Client()
        response = client.get(reverse('imageattachments:image_attachment_detail', kwargs={'slug': 'unknown-image'}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
