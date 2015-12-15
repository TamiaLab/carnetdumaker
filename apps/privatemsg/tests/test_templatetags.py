"""
Tests suite for the template tags of the notifications app.
"""

from django.test import TestCase
from django.template import (engines,
                             TemplateSyntaxError)
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import PrivateMessage


class PrivateMessagesTemplateTagsTestCase(TestCase):
    """
    Tests suite for the views.
    """

    def setUp(self):
        """
        Create a new user named "johndoe" with password "illpassword".
        """
        self.user1 = get_user_model().objects.create_user(username='johndoe',
                                                          password='illpassword',
                                                          email='john.doe@example.com')
        self.user2 = get_user_model().objects.create_user(username='johnsmith',
                                                          password='illpassword',
                                                          email='john.smith@example.com')
        self.msg1 = PrivateMessage.objects.create(sender=self.user2,
                                                  recipient=self.user1,
                                                  subject='Test 1',
                                                  body='Test 1')
        self.msg2 = PrivateMessage.objects.create(sender=self.user1,
                                                  recipient=self.user2,
                                                  subject='Test 2',
                                                  body='Test 2')
        self.msg3 = PrivateMessage.objects.create(sender=self.user2,
                                                  recipient=self.user1,
                                                  subject='Test 3',
                                                  body='Test 3',
                                                  read_at=timezone.now())

    def test_inbox_count_include_tag(self):
        """
        Test if the ``inbox_count`` template tag work when used as an include tag.
        """
        template_code = "{% load privatemsg %}{% inbox_count %}"
        template = engines['django'].from_string(template_code)
        html = template.render({'user': self.user1})
        self.assertEqual('1', html)

    def test_inbox_count_assignment_tag(self):
        """
        Test if the ``inbox_count`` template tag work when used as an assignment tag.
        """
        template_code = "{% load privatemsg %}{% inbox_count as foobar %}#{{ foobar }}"
        template = engines['django'].from_string(template_code)
        html = template.render({'user': self.user1})
        self.assertEqual('#1', html)

    def test_inbox_count_bad_argc(self):
        """
        Test if the ``inbox_count`` template tag raise error on bad arguments count.
        """
        with self.assertRaises(TemplateSyntaxError):
            template_code = "{% load privatemsg %}{% inbox_count 1 2 3 4 %}"
            template = engines['django'].from_string(template_code)
            template.render({'user': self.user1})

    def test_inbox_count_bad_argv(self):
        """
        Test if the ``inbox_count`` template tag raise error on bad arguments placement.
        """
        with self.assertRaises(TemplateSyntaxError):
            template_code = "{% load privatemsg %}{% inbox_count foo bar %}"
            template = engines['django'].from_string(template_code)
            template.render({'user': self.user1})
