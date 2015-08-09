"""
Admin views for the log watcher app.
"""

from django.contrib import admin

from .models import LogEvent


class LogEventAdmin(admin.ModelAdmin):
    """
    Admin form for the ``LogEvent`` data model.
    """

    list_display = ('event_date',
                    'type',
                    'username',
                    'ip_address')

    search_fields = ('username',
                     'ip_address')

    list_filter = ('type',
                   'event_date')


admin.site.register(LogEvent, LogEventAdmin)
