# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnouncementTag',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Slug')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name_plural': 'Announcement tags',
                'verbose_name': 'Announcement tag',
            },
        ),
        migrations.CreateModel(
            name='AnnouncementTwitterCrossPublication',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('tweet_id', models.CharField(max_length=255, db_index=True, verbose_name='Tweet ID')),
                ('pub_date', models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='Creation date')),
            ],
            options={
                'verbose_name_plural': 'Twitter cross-publications',
                'ordering': ('-pub_date',),
                'verbose_name': 'Twitter cross-publication',
                'get_latest_by': 'pub_date',
            },
        ),
        migrations.AddField(
            model_name='announcement',
            name='content_text',
            field=models.TextField(default='', verbose_name='Content (raw text)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='announcement',
            name='last_modification_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 9, 12, 21, 7, 930820, tzinfo=utc), verbose_name='Last modification date', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='announcementtwittercrosspublication',
            name='announcement',
            field=models.ForeignKey(verbose_name='Announcement', related_name='twitter_pubs', to='announcements.Announcement'),
        ),
        migrations.AddField(
            model_name='announcement',
            name='tags',
            field=models.ManyToManyField(related_name='announcements', blank=True, verbose_name="Announcement's tags", to='announcements.AnnouncementTag'),
        ),
    ]
