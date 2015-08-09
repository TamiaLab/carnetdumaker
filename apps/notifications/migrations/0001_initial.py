# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.tools.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('notification_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Notification date')),
                ('unread', models.BooleanField(default=True, verbose_name='Unread')),
                ('dismiss_code', models.CharField(default='', editable=False, db_index=True, max_length=255, verbose_name='Dismiss code')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('message', models.TextField(verbose_name='Message (plain text)')),
                ('message_html', models.TextField(verbose_name='Message (raw HTML)')),
            ],
            options={
                'ordering': ('-notification_date',),
                'verbose_name_plural': 'Notifications',
                'get_latest_by': 'notification_date',
                'verbose_name': 'Notification',
            },
        ),
        migrations.CreateModel(
            name='NotificationsUserProfile',
            fields=[
                ('user', apps.tools.fields.AutoOneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, related_name='notifications_profile', editable=False, primary_key=True, verbose_name='Related user')),
                ('send_mail_on_new_notification', models.BooleanField(default=True, verbose_name='Send mail on new notification')),
            ],
            options={
                'verbose_name_plural': 'Notification user profiles',
                'verbose_name': 'Notification user profile',
            },
        ),
        migrations.AddField(
            model_name='notification',
            name='recipient',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='notifications', verbose_name='Recipient'),
        ),
    ]
