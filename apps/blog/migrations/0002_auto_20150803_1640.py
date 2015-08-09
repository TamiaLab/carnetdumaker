# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='related_forum_thread',
            field=models.ForeignKey(null=True, to='forum.ForumThread', related_name='+', verbose_name='Related forum thread', blank=True, default=None, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(to='blog.ArticleTag', related_name='articles', blank=True, verbose_name="Article's tags"),
        ),
        migrations.AlterUniqueTogether(
            name='articlecategory',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
