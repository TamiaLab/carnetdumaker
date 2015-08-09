# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannedEmail',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('email', models.CharField(unique=True, db_index=True, max_length=280, verbose_name='Banned email')),
            ],
            options={
                'verbose_name_plural': 'Banned emails',
                'verbose_name': 'Banned email',
            },
        ),
        migrations.CreateModel(
            name='BannedUsername',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('username', models.CharField(unique=True, db_index=True, max_length=140, verbose_name='Banned username')),
            ],
            options={
                'verbose_name_plural': 'Banned usernames',
                'verbose_name': 'Banned username',
            },
        ),
        migrations.CreateModel(
            name='UserRegistrationProfile',
            fields=[
                ('user', models.OneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, related_name='+', editable=False, primary_key=True, verbose_name='Related user')),
                ('activation_key', models.CharField(max_length=20, db_index=True, verbose_name='Activation key')),
                ('activation_key_used', models.BooleanField(default=False, verbose_name='Activation key used')),
                ('last_key_mailing_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last key mailing date')),
            ],
            options={
                'verbose_name_plural': 'User registration profiles',
                'verbose_name': 'User registration profile',
            },
        ),
    ]
