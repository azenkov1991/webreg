from django.contrib import admin
from mixins.admin import safe_delete_mixin_admin
from .models import *

@safe_delete_mixin_admin
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name'
    )
    search_fields = ('code', 'name')
    list_filter = ('level',)

class MKBDiagnosAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name'
    )
    search_fields = ('code', 'name')
    list_editable = ('name', )

admin.site.register(OKMUService, ServiceAdmin)
admin.site.register(MKBDiagnos, MKBDiagnosAdmin)
