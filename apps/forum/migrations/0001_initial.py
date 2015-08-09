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
            name='Forum',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug')),
                ('slug_hierarchy', models.SlugField(unique=True, max_length=1023, verbose_name='Slug hierarchy')),
                ('logo', apps.tools.fields.AutoResizingImageField(null=True, upload_to='forum_logo', blank=True, default=None, verbose_name='Logo')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('private', models.BooleanField(default=False, verbose_name='Private')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('ordering', models.IntegerField(default=1, db_index=True, verbose_name='Ordering')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', models.ForeignKey(null=True, to='forum.Forum', related_name='children', verbose_name='Parent forum', blank=True, default=None)),
            ],
            options={
                'ordering': ('ordering', 'title'),
                'verbose_name': 'Forum',
                'verbose_name_plural': 'Forums',
                'permissions': (('can_see_private_forum', 'Can see private forum'),),
            },
        ),
        migrations.CreateModel(
            name='ForumSubscription',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('forum', models.ForeignKey(to='forum.Forum', editable=False, related_name='subscribers', verbose_name='Related forum')),
            ],
            options={
                'verbose_name_plural': 'Forum subscriptions',
                'verbose_name': 'Forum subscription',
            },
        ),
        migrations.CreateModel(
            name='ForumThread',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug')),
                ('sticky', models.BooleanField(default=False, verbose_name='Sticky')),
                ('global_sticky', models.BooleanField(default=False, verbose_name='Global sticky')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('resolved', models.BooleanField(default=False, verbose_name='Resolved')),
                ('locked', models.BooleanField(default=False, verbose_name='Locked')),
                ('deleted_at', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Deletion date')),
            ],
            options={
                'ordering': ('-last_post__last_modification_date', 'title'),
                'verbose_name_plural': 'Forum threads',
                'get_latest_by': 'last_post__last_modification_date',
                'verbose_name': 'Forum thread',
            },
        ),
        migrations.CreateModel(
            name='ForumThreadPost',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('pub_date', models.DateTimeField(db_index=True, verbose_name='Publication date')),
                ('last_modification_date', models.DateTimeField(db_index=True, verbose_name='Last modification date')),
                ('content', apps.txtrender.fields.RenderTextField(verbose_name='Content')),
                ('content_html', models.TextField(verbose_name='Content (raw HTML)')),
                ('author_ip_address', models.GenericIPAddressField(default=None, blank=True, null=True, verbose_name='Author IP address')),
                ('deleted_at', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Deletion date')),
            ],
            options={
                'ordering': ('-pub_date',),
                'verbose_name': 'Forum post',
                'verbose_name_plural': 'Forum posts',
                'get_latest_by': 'pub_date',
                'permissions': (('can_see_ip_address', 'Can see IP address'),),
            },
        ),
        migrations.CreateModel(
            name='ForumThreadSubscription',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('thread', models.ForeignKey(to='forum.ForumThread', editable=False, related_name='subscribers', verbose_name='Related thread')),
            ],
            options={
                'verbose_name_plural': 'Forum thread subscriptions',
                'verbose_name': 'Forum thread subscription',
            },
        ),
        migrations.CreateModel(
            name='ForumUserProfile',
            fields=[
                ('user', apps.tools.fields.AutoOneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, related_name='forum_profile', editable=False, primary_key=True, verbose_name='Related user')),
                ('notify_of_reply_by_default', models.BooleanField(default=True, verbose_name='Notify me of new reply by default')),
                ('last_post_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last post date')),
            ],
            options={
                'verbose_name_plural': 'Forum user profiles',
                'verbose_name': 'Forum user profile',
            },
        ),
        migrations.CreateModel(
            name='ReadForumThreadTracker',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('last_read_date', models.DateTimeField(verbose_name='Last read date')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('thread', models.ForeignKey(to='forum.ForumThread', editable=False, related_name='+', verbose_name='Related forum thread')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='+', verbose_name='Related user')),
            ],
            options={
                'verbose_name_plural': 'Read forum thread trackers',
                'verbose_name': 'Read forum thread tracker',
            },
        ),
        migrations.CreateModel(
            name='ReadForumTracker',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('last_read_date', models.DateTimeField(verbose_name='Last read date')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('forum', models.ForeignKey(to='forum.Forum', editable=False, related_name='+', verbose_name='Related forum')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='+', verbose_name='Related user')),
            ],
            options={
                'verbose_name_plural': 'Read forum trackers',
                'verbose_name': 'Read forum tracker',
            },
        ),
        migrations.AddField(
            model_name='forumthreadsubscription',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='forum_thread_subscriptions', verbose_name='Subscriber'),
        ),
        migrations.AddField(
            model_name='forumthreadpost',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='forum_posts', verbose_name='Author'),
        ),
        migrations.AddField(
            model_name='forumthreadpost',
            name='last_modification_by',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+', verbose_name='Last modification by', blank=True, default=None, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='forumthreadpost',
            name='parent_thread',
            field=models.ForeignKey(null=True, to='forum.ForumThread', related_name='posts', verbose_name='Parent thread', blank=True, default=None),
        ),
        migrations.AddField(
            model_name='forumthread',
            name='first_post',
            field=models.ForeignKey(to='forum.ForumThreadPost', related_name='first_post_of+', verbose_name='First post'),
        ),
        migrations.AddField(
            model_name='forumthread',
            name='last_post',
            field=models.ForeignKey(to='forum.ForumThreadPost', related_name='last_post_of+', verbose_name='Last post'),
        ),
        migrations.AddField(
            model_name='forumthread',
            name='parent_forum',
            field=models.ForeignKey(to='forum.Forum', related_name='threads', verbose_name='Parent forum'),
        ),
        migrations.AddField(
            model_name='forumsubscription',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='forum_subscriptions', verbose_name='Subscriber'),
        ),
        migrations.AlterUniqueTogether(
            name='readforumtracker',
            unique_together=set([('forum', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='readforumthreadtracker',
            unique_together=set([('thread', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='forumthreadsubscription',
            unique_together=set([('thread', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='forumsubscription',
            unique_together=set([('forum', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='forum',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
