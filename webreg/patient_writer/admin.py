from django.contrib import admin
from .models import SpecializationConfig, SlotTypeConfig, DepartmentConfig, ClinicConfig, SpecialistConfig


class SpecializationConfigInline(admin.TabularInline):
    model = SpecializationConfig
    filter_horizontal = ('slot_types',)
    raw_id_fields = ('service', )
    extra = 0


class DepartamentConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'city', 'min_age', 'max_age')
    search_fields = ('name',)
    inlines = (SpecializationConfigInline,)

    def get_fieldsets(self, request, obj=None):
        interval_fields = [
            'day_start_offset', 'today_time_interval',
            'day_range', 'min_age', 'max_age',
        ]
        phone_fields = ['phone', 'phone2']
        base_field = [
            ('Подразделение', {'fields': ['department']}),
            ('Интервалы', {'fields': interval_fields, }),
            ('Телефоны', {'fields': phone_fields, }),
            ('Прочее', {'fields': ['order']}),
        ]
        return base_field

    def city(self, instance):
        return instance.department.clinic.city
    city.short_description = "Город"


class SlotTypeConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_age', 'max_age')

    def name(self, instance):
        return instance.slot_type.name
    name.short_description = "Имя"


class SpecialistConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'service', 'service2', )
    raw_id_fields = ('service', 'service2')

admin.site.register(DepartmentConfig, DepartamentConfigAdmin)
admin.site.register(SlotTypeConfig, SlotTypeConfigAdmin)
admin.site.register(ClinicConfig, admin.ModelAdmin)
admin.site.register(SpecialistConfig, SpecialistConfigAdmin)
