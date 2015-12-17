# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userregistrationprofile',
            options={'verbose_name_plural': 'User registration profiles', 'ordering': ('creation_date',), 'get_latest_by': 'creation_date', 'verbose_name': 'User registration profile'},
        ),
        migrations.AddField(
            model_name='userregistrationprofile',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 12, 16, 15, 54, 6, 534958, tzinfo=utc), verbose_name='Registration date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bannedemail',
            name='email',
            field=models.CharField(max_length=254, db_index=True, verbose_name='Banned email', unique=True),
        ),
        migrations.AlterField(
            model_name='bannedusername',
            name='username',
            field=models.CharField(max_length=32, db_index=True, verbose_name='Banned username', unique=True),
        ),
        migrations.AlterField(
            model_name='userregistrationprofile',
            name='activation_key',
            field=models.CharField(max_length=32, db_index=True, verbose_name='Activation key'),
        ),
    ]
