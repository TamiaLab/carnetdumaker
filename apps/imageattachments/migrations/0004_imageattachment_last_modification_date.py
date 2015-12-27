# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('imageattachments', '0003_auto_20151214_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageattachment',
            name='last_modification_date',
            field=models.DateTimeField(verbose_name='Last modification date', default=datetime.datetime(2015, 12, 27, 14, 53, 7, 634291, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
