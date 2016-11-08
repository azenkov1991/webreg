from django.contrib import admin
from .models import *


class QmsDBAdmin(admin.ModelAdmin):
    pass
# Register your models here.
admin.site.register(QmsDB, QmsDBAdmin)
