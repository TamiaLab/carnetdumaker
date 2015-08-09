# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.txtrender.fields
import apps.tools.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation date')),
                ('last_content_modification_date', models.DateTimeField(default=None, null=True, editable=False, blank=True, db_index=True, verbose_name='Last content modification date')),
                ('pub_date', models.DateTimeField(default=None, blank=True, db_index=True, null=True, verbose_name='Publication date')),
                ('type', models.CharField(choices=[('default', 'Default'), ('success', 'Success'), ('info', 'Information'), ('warning', 'Warning'), ('danger', 'Danger')], default='default', max_length=10, verbose_name='Type')),
                ('site_wide', models.BooleanField(default=False, verbose_name='Broadcast all over the site')),
                ('content', apps.txtrender.fields.RenderTextField(verbose_name='Content')),
                ('content_html', models.TextField(verbose_name='Content (raw HTML)')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='authored_announcements', verbose_name='Author')),
            ],
            options={
                'ordering': ('-pub_date',),
                'verbose_name': 'Announcement',
                'verbose_name_plural': 'Announcements',
                'get_latest_by': 'pub_date',
                'permissions': (('can_see_preview', 'Can see any announcements in preview'),),
            },
            bases=(apps.tools.models.ModelDiffMixin, models.Model),
        ),
    ]
