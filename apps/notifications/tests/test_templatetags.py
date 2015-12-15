"""
Test suite for the template tags of the notifications app.
"""

from django.test import TestCase
from django.template import (engines,
                             TemplateSyntaxError)
from django.contrib.auth import get_user_model

from ..models import Notification


class NotificationsTemplateTagsTestCase(TestCase):
    """
    Test suite for the views.
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
        self.notif1 = Notification.objects.create(recipient=self.user1,
                                                  title='Test 1',
                                                  message='Test 1',
                                                  message_html='<p>Test 1</p>')
        self.notif2 = Notification.objects.create(recipient=self.user2,
                                                  title='Test 2',
                                                  message='Test 2',
                                                  message_html='<p>Test 2</p>')
        self.notif3 = Notification.objects.create(recipient=self.user1,
                                                  title='Test 3',
                                                  message='Test 3',
                                                  message_html='<p>Test 3</p>',
                                                  unread=False)

    def test_notifications_count_include_tag(self):
        """
        Test if the ``notifications_count`` template tag work when used as an include tag.
        """
        template_code = "{% load notifications %}{% notifications_count %}"
        template = engines['django'].from_string(template_code)
        html = template.render({'user': self.user1})
        self.assertEqual('1', html)

    def test_notifications_count_assignment_tag(self):
        """
        Test if the ``notifications_count`` template tag work when used as an assignment tag.
        """
        template_code = "{% load notifications %}{% notifications_count as foobar %}#{{ foobar }}"
        template = engines['django'].from_string(template_code)
        html = template.render({'user': self.user1})
        self.assertEqual('#1', html)

    def test_notifications_count_bad_argc(self):
        """
        Test if the ``notifications_count`` template tag raise error on bad arguments count.
        """
        with self.assertRaises(TemplateSyntaxError):
            template_code = "{% load notifications %}{% notifications_count 1 2 3 4 %}"
            template = engines['django'].from_string(template_code)
            template.render({'user': self.user1})

    def test_notifications_count_bad_argv(self):
        """
        Test if the ``notifications_count`` template tag raise error on bad arguments placement.
        """
        with self.assertRaises(TemplateSyntaxError):
            template_code = "{% load notifications %}{% notifications_count foo bar %}"
            template = engines['django'].from_string(template_code)
            template.render({'user': self.user1})
