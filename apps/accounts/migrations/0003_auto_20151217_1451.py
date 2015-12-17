# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.txtrender.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20151209_1320'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'User profile', 'ordering': ('-user__is_staff', 'user__username'), 'verbose_name_plural': 'User profiles', 'permissions': (('allow_titles_in_biography', 'Allow titles in biography'), ('allow_alerts_box_in_biography', 'Allow alerts box in biography'), ('allow_text_colors_in_biography', 'Allow coloured text in biography'), ('allow_cdm_extra_in_biography', 'Allow CDM extra in biography'), ('allow_raw_link_in_biography', 'Allow raw link (without forcing nofollow) in biography'), ('allow_code_blocks_in_signature', 'Allow code blocks in signature'), ('allow_text_colors_in_signature', 'Allow coloured text in signature'), ('allow_lists_in_signature', 'Allow lists in signature'), ('allow_tables_in_signature', 'Allow tables in signature'), ('allow_quotes_in_signature', 'Allow quotes in signature'), ('allow_medias_in_signature', 'Allow medias in signature'), ('allow_cdm_extra_in_signature', 'Allow CDM extra in signature'), ('allow_raw_link_in_signature', 'Allow raw link (without forcing nofollow) in signature'))},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='signature',
            field=apps.txtrender.fields.RenderTextField(max_length=255, verbose_name='Signature'),
        ),
    ]
