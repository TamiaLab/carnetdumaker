# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20151227_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='biography_text',
            field=models.TextField(editable=False, verbose_name='Biography (raw text)', blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='signature_text',
            field=models.TextField(editable=False, verbose_name='Signature (raw text)', blank=True, default=''),
        ),
    ]
