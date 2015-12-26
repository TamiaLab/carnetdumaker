# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import apps.txtrender.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_article_content_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='description_html',
            field=models.TextField(verbose_name='Description (raw HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='description_text',
            field=models.TextField(verbose_name='Description (raw text)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='footnotes_html',
            field=models.TextField(verbose_name='Footnotes (raw HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='summary_html',
            field=models.TextField(verbose_name='Summary (raw HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='articlecategory',
            name='description_html',
            field=models.TextField(verbose_name='Description (raw HTML)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='articlecategory',
            name='description_text',
            field=models.TextField(verbose_name='Description (raw text)', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='description',
            field=apps.txtrender.fields.RenderTextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='article',
            name='license',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_NULL, null=True, to='licenses.License', blank=True, verbose_name='License', related_name='articles'),
        ),
        migrations.AlterField(
            model_name='articlecategory',
            name='description',
            field=apps.txtrender.fields.RenderTextField(verbose_name='Description'),
        ),
    ]
