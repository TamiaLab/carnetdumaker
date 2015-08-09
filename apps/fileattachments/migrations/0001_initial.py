# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import apps.fileattachments.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileAttachment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('object_id', models.PositiveIntegerField()),
                ('file', models.FileField(verbose_name='File', upload_to=apps.fileattachments.models._upload_to_file_attachment)),
                ('size', models.IntegerField(verbose_name='File size')),
                ('filename', models.CharField(max_length=1024, verbose_name='Original filename', blank=True)),
                ('mimetype', models.CharField(max_length=255, verbose_name='Content type')),
                ('upload_date', models.DateTimeField(auto_now_add=True, verbose_name='Upload date')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'File attachments',
                'verbose_name': 'File attachment',
                'ordering': ('-upload_date', 'filename'),
                'get_latest_by': 'upload_date',
            },
        ),
    ]
