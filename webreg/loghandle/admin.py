from django.contrib import admin
from .models import *


class LogModelAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'session_key', 'level', 'message')
    list_filter = ('level', 'date', 'logger_name')
    search_fields = ('message', 'session_key')


class UserActionAdmin(admin.ModelAdmin):
    list_filter = ('date', 'action')
    readonly_fields = ('session_key', 'user', 'patient', 'action', 'info')
    exclude = ('patient_id', 'user_id')
    list_display = ('date', 'time', 'session_key', 'user', 'patient_id', 'patient', 'action')
    search_fields = ('patient_id', 'session_key')

admin.site.register(LogModel, LogModelAdmin)
admin.site.register(UserAction, UserActionAdmin)

