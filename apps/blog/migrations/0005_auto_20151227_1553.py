# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20151226_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='last_modification_date',
            field=models.DateTimeField(verbose_name='Last modification date', default=datetime.datetime(2015, 12, 27, 14, 52, 53, 577670, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='articlecategory',
            name='last_modification_date',
            field=models.DateTimeField(verbose_name='Last modification date', default=datetime.datetime(2015, 12, 27, 14, 52, 56, 969848, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='articlenote',
            name='description_text',
            field=models.TextField(verbose_name='Description (raw text)', default=datetime.datetime(2015, 12, 27, 14, 52, 59, 921597, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='articletag',
            name='last_modification_date',
            field=models.DateTimeField(verbose_name='Last modification date', default=datetime.datetime(2015, 12, 27, 14, 53, 3, 82086, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='articlerevision',
            name='revision_author',
            field=models.ForeignKey(related_name='+', null=True, blank=True, default=None, editable=False, verbose_name='Revision author', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
