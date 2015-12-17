# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('privatemsg', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatemessage',
            name='body_text',
            field=models.TextField(default='', verbose_name='Message (raw text)'),
            preserve_default=False,
        ),
    ]
