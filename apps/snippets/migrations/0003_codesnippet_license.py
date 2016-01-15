# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0003_license_description_text'),
        ('snippets', '0002_auto_20151217_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='codesnippet',
            name='license',
            field=models.ForeignKey(to='licenses.License', null=True, verbose_name='License', default=None, related_name='snippets', blank=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
