# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20150803_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='content_text',
            field=models.TextField(verbose_name='Content (raw text)', default=''),
            preserve_default=False,
        ),
    ]
