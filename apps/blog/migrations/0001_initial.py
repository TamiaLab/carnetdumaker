# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.tools.fields
import apps.txtrender.fields
from django.conf import settings
import apps.tools.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('licenses', '0001_initial'),
        ('imageattachments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('subtitle', models.CharField(default='', blank=True, max_length=255, verbose_name='Subtitle')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('deleted', 'Deleted')], max_length=10, db_index=True, default='draft', verbose_name='Status')),
                ('network_publish', models.BooleanField(default=True, verbose_name='Publish on other networks')),
                ('featured', models.BooleanField(default=False, verbose_name='Featured')),
                ('heading_img', apps.tools.fields.AutoResizingImageField(null=True, upload_to='headings/', blank=True, default=None, verbose_name='Heading image')),
                ('thumbnail_img', apps.tools.fields.AutoResizingImageField(null=True, upload_to='headings_thumbnail/', blank=True, default=None, verbose_name='Thumbnail image')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('last_content_modification_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last content modification date')),
                ('pub_date', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Publication date')),
                ('expiration_date', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Expiration date')),
                ('membership_required', models.BooleanField(default=False, verbose_name='Membership required')),
                ('membership_required_expiration_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Membership required expiration date')),
                ('auto_create_related_forum_thread', models.BooleanField(default=True, verbose_name='Auto create related forum thread')),
                ('display_img_gallery', models.BooleanField(default=False, verbose_name='Display the image gallery')),
                ('content', apps.txtrender.fields.RenderTextField(verbose_name='Content')),
                ('content_html', models.TextField(verbose_name='Content (raw HTML)')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='authored_articles', verbose_name='Author')),
            ],
            options={
                'ordering': ('-featured', '-creation_date'),
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'permissions': (('can_see_preview', 'Can see article in preview'),),
            },
            bases=(apps.tools.models.ModelDiffMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug')),
                ('slug_hierarchy', models.SlugField(unique=True, max_length=1023, verbose_name='Slug hierarchy')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('logo', apps.tools.fields.AutoResizingImageField(null=True, upload_to='category_logos/', blank=True, default=None, verbose_name='Logo')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', models.ForeignKey(null=True, to='blog.ArticleCategory', related_name='children', verbose_name='Parent category', blank=True, default=None)),
            ],
            options={
                'verbose_name_plural': 'Article categories',
                'verbose_name': 'Article category',
            },
        ),
        migrations.CreateModel(
            name='ArticleNote',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title_internal', models.CharField(max_length=255, verbose_name='Title (for internal use)')),
                ('title', models.CharField(default='', blank=True, max_length=255, verbose_name='Title')),
                ('description', apps.txtrender.fields.RenderTextField(verbose_name='Description')),
                ('description_html', models.TextField(verbose_name='Description (raw HTML)')),
                ('type', models.CharField(choices=[('default', 'Default'), ('success', 'Success'), ('info', 'Information'), ('warning', 'Warning'), ('danger', 'Danger')], default='default', max_length=10, verbose_name='Note type')),
            ],
            options={
                'verbose_name_plural': 'Article notes',
                'verbose_name': 'Article note',
            },
        ),
        migrations.CreateModel(
            name='ArticleRevision',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(editable=False, max_length=255, verbose_name='Title')),
                ('subtitle', models.CharField(default='', blank=True, editable=False, max_length=255, verbose_name='Subtitle')),
                ('description', models.TextField(blank=True, editable=False, default='', verbose_name='Description')),
                ('content', models.TextField(editable=False, verbose_name='Content')),
                ('revision_minor_change', models.BooleanField(editable=False, default=False, verbose_name='Minor changes')),
                ('revision_description', models.TextField(blank=True, editable=False, default='', verbose_name='Revision description')),
                ('revision_date', models.DateTimeField(auto_now_add=True, verbose_name='Revision date')),
                ('related_article', models.ForeignKey(to='blog.Article', editable=False, related_name='revisions', verbose_name='Related article')),
                ('revision_author', models.ForeignKey(default=None, null=True, to=settings.AUTH_USER_MODEL, editable=False, related_name='+', blank=True, verbose_name='Revision author')),
            ],
            options={
                'ordering': ('-revision_date',),
                'verbose_name_plural': 'Article revisions',
                'get_latest_by': 'revision_date',
                'verbose_name': 'Article revision',
            },
        ),
        migrations.CreateModel(
            name='ArticleTag',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Article tags',
                'verbose_name': 'Article tag',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='categories',
            field=models.ManyToManyField(to='blog.ArticleCategory', related_name='articles', blank=True, verbose_name="Article's categories"),
        ),
        migrations.AddField(
            model_name='article',
            name='follow_up_of',
            field=models.ManyToManyField(to='blog.Article', related_name='follow_up_articles', blank=True, verbose_name='Follow up of'),
        ),
        migrations.AddField(
            model_name='article',
            name='foot_notes',
            field=models.ManyToManyField(to='blog.ArticleNote', related_name='foot_uses+', blank=True, verbose_name="Article's footer notes"),
        ),
        migrations.AddField(
            model_name='article',
            name='head_notes',
            field=models.ManyToManyField(to='blog.ArticleNote', related_name='head_uses+', blank=True, verbose_name="Article's heading notes"),
        ),
        migrations.AddField(
            model_name='article',
            name='img_attachments',
            field=models.ManyToManyField(to='imageattachments.ImageAttachment', related_name='articles', blank=True, verbose_name="Article's image attachments"),
        ),
        migrations.AddField(
            model_name='article',
            name='license',
            field=models.ForeignKey(null=True, to='licenses.License', related_name='articles', verbose_name='License', blank=True, default=None),
        ),
        migrations.AddField(
            model_name='article',
            name='related_articles',
            field=models.ManyToManyField(to='blog.Article', related_name='related_articles_reverse', blank=True, verbose_name='Related articles'),
        ),
    ]
