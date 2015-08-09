# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import apps.tools.fields
import apps.txtrender.fields
from django.conf import settings
import apps.tools.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppComponent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name (for display)')),
                ('internal_name', models.CharField(max_length=255, verbose_name='Name (for internal use)')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
            ],
            options={
                'verbose_name_plural': 'Application components',
                'verbose_name': 'Application component',
            },
        ),
        migrations.CreateModel(
            name='BugTrackerUserProfile',
            fields=[
                ('user', apps.tools.fields.AutoOneToOneField(serialize=False, to=settings.AUTH_USER_MODEL, related_name='bugtracker_profile', editable=False, primary_key=True, verbose_name='Related user')),
                ('notify_of_new_issue', models.BooleanField(default=False, verbose_name='Notify me of new issue')),
                ('notify_of_reply_by_default', models.BooleanField(default=True, verbose_name='Notify me of new reply by default')),
                ('last_comment_date', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Last comment date')),
            ],
            options={
                'verbose_name_plural': 'Bug tracker user profiles',
                'verbose_name': 'Bug tracker user profile',
            },
        ),
        migrations.CreateModel(
            name='IssueChange',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('change_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Change date')),
                ('field_name', models.CharField(max_length=255, verbose_name='Field name')),
                ('old_value', models.TextField(blank=True, default='', verbose_name='Old value')),
                ('new_value', models.TextField(blank=True, default='', verbose_name='New value')),
            ],
            options={
                'ordering': ('change_date',),
                'verbose_name_plural': 'Issue changes',
                'get_latest_by': 'change_date',
                'verbose_name': 'Issue change',
            },
        ),
        migrations.CreateModel(
            name='IssueComment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Publication date')),
                ('body', apps.txtrender.fields.RenderTextField(verbose_name='Comment text')),
                ('body_html', models.TextField(verbose_name='Comment text (raw HTML)')),
                ('author_ip_address', models.GenericIPAddressField(default=None, blank=True, null=True, verbose_name='Author IP address')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='issues_comments', verbose_name='Comment author')),
            ],
            options={
                'ordering': ('pub_date',),
                'verbose_name_plural': 'Issue comments',
                'get_latest_by': 'pub_date',
                'verbose_name': 'Issue comment',
            },
        ),
        migrations.CreateModel(
            name='IssueTicket',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', apps.txtrender.fields.RenderTextField(verbose_name='Description')),
                ('description_html', models.TextField(verbose_name='Description (raw HTML)')),
                ('submission_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Submission date')),
                ('last_modification_date', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last modification date')),
                ('status', models.CharField(choices=[('open', 'Issue open'), ('reopen', 'Issue reopened'), ('needetails', 'Need more details'), ('confirmed', 'Issue confirmed'), ('workon', 'Working on'), ('deferred', 'Deferred (no time for that now)'), ('duplicate', 'Duplicate issue'), ('wontfix', "Won't fix (sorry)"), ('closed', 'Closed'), ('fixed', 'Fixed')], max_length=10, db_index=True, default='open', verbose_name='Status')),
                ('priority', models.CharField(choices=[('godzilla', "Godzilla (We're doomed!)"), ('critical', 'Critical (serious bug, need quick hotfix)'), ('major', 'Major (serious bug)'), ('minor', 'Minor (simple bug)'), ('trivial', 'Trivial (cosmetic issues)'), ('needreview', 'Need review'), ('feature', 'Feature request'), ('wishlist', 'Wishlist request'), ('invalid', 'Invalid'), ('notmyfault', 'Not my fault')], max_length=10, db_index=True, default='needreview', verbose_name='Priority')),
                ('difficulty', models.CharField(choices=[('bigoops', 'Design errors - back to the drawing board'), ('important', 'Important'), ('normal', 'Normal'), ('low', 'Low'), ('someday', 'Optional (will fix someday)')], max_length=10, db_index=True, default='normal', verbose_name='Difficulty')),
                ('submitter_ip_address', models.GenericIPAddressField(default=None, blank=True, null=True, verbose_name='Submitter IP address')),
                ('assigned_to', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='assigned_issues', verbose_name='Assigned to', blank=True, default=None, on_delete=django.db.models.deletion.SET_NULL)),
                ('component', models.ForeignKey(null=True, to='bugtracker.AppComponent', related_name='tickets', blank=True, on_delete=django.db.models.deletion.SET_NULL, default=None)),
                ('submitter', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='submitted_issues', verbose_name='Submitter')),
            ],
            options={
                'ordering': ('-submission_date', 'priority', 'status', 'title'),
                'verbose_name_plural': 'Issue tickets',
                'get_latest_by': 'submission_date',
                'verbose_name': 'Issue ticket',
            },
            bases=(apps.tools.models.ModelDiffMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IssueTicketSubscription',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('issue', models.ForeignKey(to='bugtracker.IssueTicket', related_name='subscribers', verbose_name='Related issue')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='ticket_subscriptions', verbose_name='Subscriber')),
            ],
            options={
                'ordering': ('-active',),
                'verbose_name_plural': 'Issue ticket subscriptions',
                'verbose_name': 'Issue ticket subscription',
            },
        ),
        migrations.AddField(
            model_name='issuecomment',
            name='issue',
            field=models.ForeignKey(to='bugtracker.IssueTicket', editable=False, related_name='comments', verbose_name='Related issue'),
        ),
        migrations.AddField(
            model_name='issuechange',
            name='comment',
            field=models.ForeignKey(to='bugtracker.IssueComment', editable=False, related_name='changes', verbose_name='Related comment'),
        ),
        migrations.AddField(
            model_name='issuechange',
            name='issue',
            field=models.ForeignKey(to='bugtracker.IssueTicket', editable=False, related_name='changes', verbose_name='Related issue'),
        ),
        migrations.AlterUniqueTogether(
            name='issueticketsubscription',
            unique_together=set([('issue', 'user')]),
        ),
    ]
