# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.txtrender.fields


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='codesnippet',
            name='description_html',
            field=models.TextField(default='', verbose_name='Description (raw HTML)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='codesnippet',
            name='description_text',
            field=models.TextField(default='', verbose_name='Description (raw text)'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='codesnippet',
            name='description',
            field=apps.txtrender.fields.RenderTextField(verbose_name='Description'),
        ),
    ]
