from django.contrib import admin
from .models import *


class QmsDBAdmin(admin.ModelAdmin):
    pass

class IdMatchingTableAdmin(admin.ModelAdmin):
    list_display = ('id','external_id')

# Register your models here.
admin.site.register(QmsDB, QmsDBAdmin)
admin.site.register(ObjectMatchingTable, QmsDBAdmin)
admin.site.register(IdMatchingTable, IdMatchingTableAdmin)
