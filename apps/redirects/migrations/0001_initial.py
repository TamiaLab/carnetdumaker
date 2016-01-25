# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Redirection',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('old_path', models.CharField(max_length=200, verbose_name='Old path', db_index=True, help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.")),
                ('new_path', models.CharField(max_length=200, default='', verbose_name='New path', blank=True, help_text="This can be either an absolute path (as above) or a full URL starting with 'http://'. Can be blank if the redirection should raise a '410 Gone' response.")),
                ('permanent_redirect', models.BooleanField(default=True, verbose_name='Permanent redirection')),
                ('active', models.BooleanField(default=True, verbose_name='Redirection enabled')),
                ('site', models.ForeignKey(to='sites.Site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'Redirect',
                'verbose_name_plural': 'Redirects',
                'ordering': ('old_path',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='redirection',
            unique_together=set([('site', 'old_path')]),
        ),
    ]
