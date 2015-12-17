# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('privatemsg', '0002_privatemessage_body_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='privatemessage',
            options={'verbose_name': 'Private message', 'ordering': ('-sent_at', 'id'), 'verbose_name_plural': 'Private messages', 'permissions': (('allow_cdm_extra', 'Allow CDM extra'),), 'get_latest_by': 'sent_at'},
        ),
    ]
