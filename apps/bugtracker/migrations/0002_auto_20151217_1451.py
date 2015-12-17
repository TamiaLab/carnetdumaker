# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bugtracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuecomment',
            name='body_text',
            field=models.TextField(verbose_name='Comment text (raw text)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issueticket',
            name='description_text',
            field=models.TextField(verbose_name='Description (raw text)', default=''),
            preserve_default=False,
        ),
    ]
