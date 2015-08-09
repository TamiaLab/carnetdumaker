# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.tools.fields
import apps.txtrender.fields


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Publication date')),
                ('legend', models.CharField(default='', blank=True, max_length=255, verbose_name='Legend')),
                ('description', apps.txtrender.fields.RenderTextField(verbose_name='Description')),
                ('description_html', models.TextField(verbose_name='Description (raw HTML)')),
                ('img_small', apps.tools.fields.ThumbnailImageField(height_field='img_small_height', width_field='img_small_width', upload_to='img_attachments/small', verbose_name='Image (small size)')),
                ('img_small_height', models.IntegerField(verbose_name='Image height (small size, in pixels)')),
                ('img_small_width', models.IntegerField(verbose_name='Image width (small size, in pixels)')),
                ('img_medium', apps.tools.fields.ThumbnailImageField(height_field='img_medium_height', width_field='img_medium_width', upload_to='img_attachments/medium', verbose_name='Image (medium size)')),
                ('img_medium_height', models.IntegerField(verbose_name='Image height (medium size, in pixels)')),
                ('img_medium_width', models.IntegerField(verbose_name='Image width (medium size, in pixels)')),
                ('img_large', apps.tools.fields.ThumbnailImageField(height_field='img_large_height', width_field='img_large_width', upload_to='img_attachments/large', verbose_name='Image (large size)')),
                ('img_large_height', models.IntegerField(verbose_name='Image height (large size, in pixels)')),
                ('img_large_width', models.IntegerField(verbose_name='Image width (large size, in pixels)')),
                ('img_original', models.ImageField(height_field='img_original_height', width_field='img_original_width', upload_to='img_attachments', verbose_name='Image (original size)')),
                ('img_original_height', models.IntegerField(verbose_name='Image height (original size, in pixels)')),
                ('img_original_width', models.IntegerField(verbose_name='Image width (original size, in pixels)')),
                ('license', models.ForeignKey(null=True, to='licenses.License', related_name='img_attachments', verbose_name='License', blank=True, default=None)),
            ],
            options={
                'ordering': ('-pub_date', 'title'),
                'verbose_name_plural': 'Image attachments',
                'get_latest_by': 'pub_date',
                'verbose_name': 'Image attachment',
            },
        ),
    ]
