"""
Tests suite for the admin views of the image attachments app.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from ..models import ImageAttachment


class ImageAttachmentAdminTestCase(TestCase):
    """
    Tests suite for the admin views.
    """

    def setUp(self):
        """
        Create some fixtures for the tests.
        """
        self.user = get_user_model().objects.create_superuser(username='johndoe',
                                                              password='illpassword',
                                                              email='john.doe@example.com')
        self.image = ImageAttachment.objects.create(title='Test 1',
                                                    slug='test-1',
                                                    description='Image 1',
                                                    img_original='fixtures/beautifulfrog.jpg')

    def test_image_list_view_available(self):
        """
        Test the availability of the "image list" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:imageattachments_imageattachment_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_image_edit_view_available(self):
        """
        Test the availability of the "edit image" view.
        """
        client = Client()
        client.login(username='johndoe', password='illpassword')
        response = client.get(reverse('admin:imageattachments_imageattachment_change', args=[self.image.pk]))
        self.assertEqual(response.status_code, 200)
