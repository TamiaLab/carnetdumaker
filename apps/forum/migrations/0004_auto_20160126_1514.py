# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20160101_1840'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumCategory',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('ordering', models.IntegerField(db_index=True, default=1, verbose_name='Ordering')),
            ],
            options={
                'ordering': ('ordering', 'title'),
                'verbose_name_plural': 'Forum categories',
                'verbose_name': 'Forum category',
            },
        ),
        migrations.AddField(
            model_name='forumthreadpost',
            name='useful',
            field=models.BooleanField(default=False, verbose_name='Useful'),
        ),
        migrations.AddField(
            model_name='forum',
            name='category',
            field=models.ForeignKey(null=True, blank=True, default=None, verbose_name='Category', to='forum.ForumCategory', related_name='forums'),
        ),
    ]
