# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DbMutexLock',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('mutex_name', models.CharField(unique=True, db_index=True, max_length=255, verbose_name='Mutex name')),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation date')),
            ],
            options={
                'ordering': ('-creation_date', 'mutex_name'),
                'verbose_name_plural': 'Mutex locks',
                'get_latest_by': 'creation_date',
                'verbose_name': 'Mutex lock',
            },
        ),
    ]
