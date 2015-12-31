# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserStrike',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('target_ip_address', models.GenericIPAddressField(default=None, verbose_name='Related IP address', null=True, db_index=True, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('expiration_date', models.DateTimeField(default=None, verbose_name='Expiration date', null=True, blank=True)),
                ('block_access', models.BooleanField(default=False, verbose_name='Block access (ban)')),
                ('internal_reason', models.TextField(verbose_name='Strike reason (internal)')),
                ('public_reason', models.TextField(default='', verbose_name='Strike reason (public)', blank=True)),
                ('author', models.ForeignKey(verbose_name='Author', to=settings.AUTH_USER_MODEL, related_name='authored_admin_strikes')),
                ('target_user', models.ForeignKey(related_name='admin_strikes', verbose_name='Related user', null=True, default=None, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ('-creation_date',),
                'get_latest_by': 'creation_date',
                'verbose_name': 'User strike',
                'verbose_name_plural': 'User strikes',
            },
        ),
    ]
