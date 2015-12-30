# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('bugtracker', '0002_auto_20151217_1451'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issueticket',
            options={'verbose_name_plural': 'Issue tickets', 'ordering': ('-submission_date', 'priority', 'status', 'title'), 'get_latest_by': 'submission_date', 'verbose_name': 'Issue ticket', 'permissions': (('allow_titles_in_ticket', 'Allow titles in issue ticket'), ('allow_alerts_box_in_ticket', 'Allow alerts box in issue ticket'), ('allow_text_colors_in_ticket', 'Allow coloured text in issue ticket'), ('allow_cdm_extra_in_ticket', 'Allow CDM extra in issue ticket'), ('allow_raw_link_in_ticket', 'Allow raw link (without forcing nofollow) in issue ticket'), ('allow_titles_in_comment', 'Allow titles in issue comment'), ('allow_alerts_box_in_comment', 'Allow alerts box in issue comment'), ('allow_text_colors_in_comment', 'Allow coloured text in issue comment'), ('allow_cdm_extra_in_comment', 'Allow CDM extra in issue comment'), ('allow_raw_link_in_comment', 'Allow raw link (without forcing nofollow) in issue comment'))},
        ),
        migrations.AddField(
            model_name='issuecomment',
            name='last_modification_date',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2015, 12, 28, 13, 24, 14, 917065, tzinfo=utc), verbose_name='Last modification date'),
            preserve_default=False,
        ),
    ]
