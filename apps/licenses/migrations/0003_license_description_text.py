# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0002_auto_20151209_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='description_text',
            field=models.TextField(verbose_name='Description (raw text)', default=''),
            preserve_default=False,
        ),
    ]
