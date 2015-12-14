# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imageattachments', '0002_auto_20151209_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageattachment',
            name='description_text',
            field=models.TextField(default='', verbose_name='Description (raw text)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imageattachment',
            name='public_listing',
            field=models.BooleanField(default=True, verbose_name='Public listing'),
        ),
    ]
