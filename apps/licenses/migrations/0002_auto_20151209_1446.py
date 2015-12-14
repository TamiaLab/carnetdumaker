# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='license',
            options={'verbose_name': 'License', 'ordering': ('name',), 'verbose_name_plural': 'Licenses'},
        ),
        migrations.AlterField(
            model_name='license',
            name='name',
            field=models.CharField(verbose_name='Name', db_index=True, max_length=255),
        ),
    ]
