# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc
import apps.txtrender.fields


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_forumthreadpost_content_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='forumthreadpost',
            options={'verbose_name': 'Forum post', 'permissions': (('can_see_ip_address', 'Can see IP address'), ('allow_titles_in_post', 'Allow titles in forum post'), ('allow_alerts_box_in_post', 'Allow alerts box in forum post'), ('allow_text_colors_in_post', 'Allow coloured text in forum post'), ('allow_cdm_extra_in_post', 'Allow CDM extra in forum post'), ('allow_raw_link_in_post', 'Allow raw link (without forcing nofollow) in forum post')), 'verbose_name_plural': 'Forum posts', 'get_latest_by': 'pub_date', 'ordering': ('-pub_date',)},
        ),
        migrations.AddField(
            model_name='forum',
            name='description_html',
            field=models.TextField(verbose_name='Description (raw HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forum',
            name='description_text',
            field=models.TextField(verbose_name='Description (raw text)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forum',
            name='last_modification_date',
            field=models.DateTimeField(verbose_name='Last modification date', auto_now=True, default=datetime.datetime(2016, 1, 1, 17, 39, 44, 851386, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forumthread',
            name='last_modification_date',
            field=models.DateTimeField(verbose_name='Last modification date', auto_now=True, default=datetime.datetime(2016, 1, 1, 17, 39, 48, 403848, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forumthreadpost',
            name='footnotes_html',
            field=models.TextField(verbose_name='Content footnotes (raw HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forumthreadpost',
            name='last_content_modification_date',
            field=models.DateTimeField(verbose_name='Last content modification date', db_index=True, default=datetime.datetime(2016, 1, 1, 17, 39, 57, 300151, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forumthreadpost',
            name='summary_html',
            field=models.TextField(verbose_name='Content summary (raw HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='forum',
            name='description',
            field=apps.txtrender.fields.RenderTextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='forumthreadpost',
            name='last_modification_date',
            field=models.DateTimeField(verbose_name='Last modification date', auto_now=True),
        ),
    ]
