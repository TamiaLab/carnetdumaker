# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import apps.txtrender.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('snippets', '0003_codesnippet_license'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeSnippetBundle',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('directory_name', models.CharField(max_length=255, verbose_name='Filename')),
                ('public_listing', models.BooleanField(default=True, verbose_name='Public listing')),
                ('description', apps.txtrender.fields.RenderTextField(verbose_name='Description')),
                ('description_html', models.TextField(verbose_name='Description (raw HTML)')),
                ('description_text', models.TextField(verbose_name='Description (raw text)')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('last_modification_date', models.DateTimeField(auto_now=True, verbose_name='Last modification date')),
                ('author', models.ForeignKey(related_name='snippets_bundle', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('snippets', models.ManyToManyField(to='snippets.CodeSnippet', verbose_name='Snippets in this bundle')),
            ],
            options={
                'verbose_name': 'Code snippets bundle',
                'verbose_name_plural': 'Code snippets bundles',
                'get_latest_by': 'creation_date',
                'ordering': ('-creation_date',),
            },
        ),
    ]
