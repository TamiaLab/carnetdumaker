# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserApiKey',
            fields=[
                ('user', models.OneToOneField(related_name='api_key', verbose_name='Related user', primary_key=True, editable=False, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('api_key', models.CharField(db_index=True, verbose_name='API key', max_length=32)),
                ('last_generation_date', models.DateTimeField(auto_now=True, verbose_name='Last generation date')),
            ],
            options={
                'verbose_name_plural': 'User API keys',
                'ordering': ('-last_generation_date',),
                'get_latest_by': 'last_generation_date',
                'verbose_name': 'User API key',
            },
        ),
    ]
