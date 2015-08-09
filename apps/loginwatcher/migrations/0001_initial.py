# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogEvent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(0, 'Login success'), (1, 'Login failed'), (2, 'Logout')], editable=False, db_index=True, verbose_name='Event')),
                ('event_date', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Date')),
                ('username', models.CharField(editable=False, db_index=True, max_length=255, verbose_name='Username')),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True, editable=False, db_index=True, verbose_name='IP address')),
            ],
            options={
                'ordering': ('-event_date',),
                'verbose_name_plural': 'Log events',
                'get_latest_by': 'event_date',
                'verbose_name': 'Log event',
            },
        ),
    ]
