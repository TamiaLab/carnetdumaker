# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('old_path', models.CharField(verbose_name='redirect from', db_index=True, max_length=200, help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.")),
                ('new_path', models.CharField(blank=True, verbose_name='redirect to', max_length=200, help_text="This can be either an absolute path (as above) or a full URL starting with 'http://'.")),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'verbose_name': 'redirect',
                'verbose_name_plural': 'redirects',
                'ordering': ('old_path',),
                'db_table': 'django_redirect',
            },
        ),
        migrations.CreateModel(
            name='Redirection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('old_path', models.CharField(verbose_name='Old path', db_index=True, max_length=200, help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.")),
                ('new_path', models.CharField(blank=True, verbose_name='New path', max_length=200, help_text="This can be either an absolute path (as above) or a full URL starting with 'http://'. Can be blank if the redirection should raise a '410 Gone' response.")),
                ('permanent_redirect', models.BooleanField(default=True, verbose_name='Permanent redirection')),
                ('active', models.BooleanField(default=True, verbose_name='Redirection enabled')),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            options={
                'verbose_name': 'Redirection',
                'ordering': ('old_path',),
                'verbose_name_plural': 'Redirections',
            },
        ),
        migrations.AlterUniqueTogether(
            name='redirection',
            unique_together=set([('site', 'old_path')]),
        ),
        migrations.AlterUniqueTogether(
            name='redirect',
            unique_together=set([('site', 'old_path')]),
        ),
    ]
