# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageattachments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imageattachment',
            options={'verbose_name': 'Image attachment', 'get_latest_by': 'pub_date', 'ordering': ('-pub_date',), 'verbose_name_plural': 'Image attachments'},
        ),
    ]
