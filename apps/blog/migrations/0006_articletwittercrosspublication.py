# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20151227_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleTwitterCrossPublication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('tweet_id', models.CharField(max_length=255, db_index=True, verbose_name='Tweet ID')),
                ('pub_date', models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='Creation date')),
                ('article', models.ForeignKey(verbose_name='Article', to='blog.Article', related_name='twitter_pubs')),
            ],
            options={
                'verbose_name_plural': 'Twitter cross-publications',
                'ordering': ('-pub_date',),
                'verbose_name': 'Twitter cross-publication',
                'get_latest_by': 'pub_date',
            },
        ),
    ]
