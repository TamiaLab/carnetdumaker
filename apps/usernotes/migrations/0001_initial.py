# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNote',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('last_modification_date', models.DateTimeField(verbose_name='Last modification date', auto_now=True)),
                ('sticky', models.BooleanField(verbose_name='Sticky', default=False)),
                ('author', models.ForeignKey(verbose_name='Author', related_name='authored_admin_notes', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(verbose_name='Related user', related_name='admin_notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User note',
                'verbose_name_plural': 'User notes',
                'ordering': ('-sticky', '-last_modification_date'),
                'get_latest_by': 'creation_date',
            },
        ),
    ]
