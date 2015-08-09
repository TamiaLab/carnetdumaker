# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.txtrender.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('logo', models.ImageField(null=True, upload_to='licenses_logo', blank=True, default=None, verbose_name='Logo')),
                ('description', apps.txtrender.fields.RenderTextField(verbose_name='Description')),
                ('description_html', models.TextField(verbose_name='Description (raw HTML)')),
                ('usage', models.TextField(blank=True, default='', verbose_name='Usage')),
                ('source_url', models.URLField(default='', blank=True, verbose_name='Source URL')),
                ('last_modification_date', models.DateTimeField(auto_now=True, verbose_name='Last modification date')),
            ],
            options={
                'verbose_name_plural': 'Licenses',
                'verbose_name': 'License',
            },
        ),
    ]
