from django.contrib import admin
from .models import *


class QmsDBAdmin(admin.ModelAdmin):
    pass


class IdMatchingTableAdmin(admin.ModelAdmin):
    list_display = ('internal_id','external_id')


class QmsUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'qqc244')


class QmsDepartmentCodeInline(admin.TabularInline):
    model = QmsDepartmentCode
    extra = 0


class QmsDepartmentAdmin(admin.ModelAdmin):
    inlines = (QmsDepartmentCodeInline,)


# Register your models here.
admin.site.register(QmsDB, QmsDBAdmin)
admin.site.register(ObjectMatchingTable, QmsDBAdmin)
admin.site.register(IdMatchingTable, IdMatchingTableAdmin)
admin.site.register(QmsUser, QmsUserAdmin)
admin.site.register(QmsDepartment, QmsDepartmentAdmin)
