# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import apps.tools.fields
import apps.txtrender.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedUser',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('last_block_date', models.DateTimeField(verbose_name='Last block date')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'ordering': ('-active', '-last_block_date'),
                'verbose_name_plural': 'Blocked users',
                'get_latest_by': 'last_block_date',
                'verbose_name': 'Blocked user',
            },
        ),
        migrations.CreateModel(
            name='PrivateMessage',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('subject', models.CharField(default='', blank=True, max_length=255, verbose_name='Subject')),
                ('body', apps.txtrender.fields.RenderTextField(verbose_name='Message')),
                ('body_html', models.TextField(verbose_name='Message (raw HTML)')),
                ('sent_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Sent at')),
                ('read_at', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Read at')),
                ('sender_deleted_at', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Sender deleted at')),
                ('recipient_deleted_at', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Recipient deleted at')),
                ('sender_permanently_deleted', models.BooleanField(default=False, verbose_name='Sender permanently deleted')),
                ('recipient_permanently_deleted', models.BooleanField(default=False, verbose_name='Recipient permanently deleted')),
                ('parent_msg', models.ForeignKey(null=True, to='privatemsg.PrivateMessage', related_name='replies', verbose_name='Parent message', blank=True, default=None, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'ordering': ('-sent_at', 'id'),
                'verbose_name_plural': 'Private messages',
                'get_latest_by': 'sent_at',
                'verbose_name': 'Private message',
            },
        ),
        migrations.CreateModel(
            name='PrivateMessageUserProfile',
            fields=[
                ('user', apps.tools.fields.AutoOneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, related_name='privatemsg_profile', editable=False, primary_key=True, verbose_name='Related user')),
                ('notify_on_new_privmsg', models.BooleanField(default=True, verbose_name='Notify me of new private message')),
                ('accept_privmsg', models.BooleanField(default=True, verbose_name='Accept incoming private message')),
                ('last_sent_private_msg_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last sent private msg date')),
            ],
            options={
                'verbose_name_plural': 'Private messages user profiles',
                'verbose_name': 'Private messages user profile',
            },
        ),
        migrations.AddField(
            model_name='privatemessage',
            name='recipient',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='privatemsg_received', verbose_name='Recipient'),
        ),
        migrations.AddField(
            model_name='privatemessage',
            name='sender',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='privatemsg_sent', verbose_name='Sender'),
        ),
        migrations.AddField(
            model_name='blockeduser',
            name='blocked_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='blockedby_users', verbose_name='Blocked user'),
        ),
        migrations.AddField(
            model_name='blockeduser',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='blocked_users', verbose_name='Related user'),
        ),
        migrations.AlterUniqueTogether(
            name='blockeduser',
            unique_together=set([('user', 'blocked_user')]),
        ),
    ]
