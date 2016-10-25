# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import OKMUService


class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name'
    )
    list_filter = ('code', 'name')
    search_fields = ('code', 'name')
    list_editable = ('name', )

admin.site.register(OKMUService, ServiceAdmin)
