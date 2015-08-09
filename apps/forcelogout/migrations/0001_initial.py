# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForceLogoutOrder',
            fields=[
                ('user', models.OneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, related_name='+', editable=False, primary_key=True, verbose_name='Related user')),
                ('order_date', models.DateTimeField(verbose_name='Logout order date')),
            ],
            options={
                'ordering': ('-order_date',),
                'verbose_name_plural': 'Logout orders',
                'get_latest_by': 'order_date',
                'verbose_name': 'Logout order',
            },
        ),
    ]
