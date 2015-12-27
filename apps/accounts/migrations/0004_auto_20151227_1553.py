# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20151217_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='biography_text',
            field=models.TextField(blank=True, verbose_name='Biography (raw HTML)', default='', editable=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='signature_text',
            field=models.TextField(blank=True, verbose_name='Signature (raw HTML)', default='', editable=False),
        ),
    ]
