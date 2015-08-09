# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentReport',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('report_date', models.DateTimeField(auto_now_add=True, verbose_name='Report date')),
                ('reason', models.CharField(default='', blank=True, max_length=255, verbose_name='Reason')),
                ('processed', models.BooleanField(default=False, verbose_name='Processed')),
                ('reporter_ip_address', models.GenericIPAddressField(default=None, blank=True, null=True, verbose_name='Reporter IP address')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('reporter', models.ForeignKey(to=settings.AUTH_USER_MODEL, editable=False, related_name='content_reports', verbose_name='Reporter')),
            ],
            options={
                'ordering': ('-report_date',),
                'verbose_name_plural': 'Content reports',
                'get_latest_by': 'report_date',
                'verbose_name': 'Content report',
            },
        ),
    ]
