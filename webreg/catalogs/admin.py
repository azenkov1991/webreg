from django.contrib import admin
from .models import *

class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name'
    )
    list_filter = ('code', 'name')
    search_fields = ('code', 'name')
    list_editable = ('name', )

admin.site.register(OKMUService, ServiceAdmin)
admin.site.register(MKBDiagnos, ServiceAdmin)
