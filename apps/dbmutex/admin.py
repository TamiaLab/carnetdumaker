"""
Admin views for the database mutex app.
"""

from django.contrib import admin

from .models import DbMutexLock


class DbMutexLockAdmin(admin.ModelAdmin):
    """
    ``DbMutexLock`` admin form.
    """

    list_display = ('mutex_name',
                    'creation_date',
                    'expired')

    list_filter = ('creation_date', )

    search_fields = ('mutex_name', )


admin.site.register(DbMutexLock, DbMutexLockAdmin)
