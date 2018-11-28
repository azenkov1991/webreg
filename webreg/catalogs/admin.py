from django.contrib import admin
from .models import *


class MKBDiagnosAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name'
    )
    search_fields = ('code', 'name')
    list_editable = ('name', )


admin.site.register(MKBDiagnos, MKBDiagnosAdmin)
