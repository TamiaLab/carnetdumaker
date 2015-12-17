# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumthreadpost',
            name='content_text',
            field=models.TextField(verbose_name='Content (raw text)', default=''),
            preserve_default=False,
        ),
    ]
