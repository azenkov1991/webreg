from django.contrib import admin
from django import forms
from main.models import *
from mixins.admin import safe_delete_mixin_admin
from main.forms import UserProfileForm


@safe_delete_mixin_admin
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name'
    )
    search_fields = ('code', 'name')
    list_filter = ('level',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'clinic')


class DepartmentInline(admin.StackedInline):
    model = Department


class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address',)
    search_fields = ('name', 'address',)
    inlines = [DepartmentInline, ]


@safe_delete_mixin_admin
class SpecialistAdmin(admin.ModelAdmin):
    list_display = (
        'fio', 'specialization', 'department',
    )
    list_display_links = ('fio', 'specialization')
    list_filter = ('department', 'specialization',)
    search_fields = ('fio',)
    raw_id_fields = ('performing_services',)
    autocomplete_lookup_fields = {
        'm2m': ['performing_services', ]
    }


class CabinetAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'name')
    list_editable = ('number', 'name')


class PatientAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'middle_name')
    list_filter = ('birth_date',)


class AppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        try:
            self.fields['service'].queryset = self.instance.cell.specialist.performing_services.all()
        except:
            self.fields['service'].queryset = Service.objects.all()


@safe_delete_mixin_admin
class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentForm
    list_display = ('date', 'specialist', 'service', 'patient')
    list_filter = ('date', 'specialist')
    search_fields = ('specialist', '-date')
    ordering = ('-date', 'specialist')
    raw_id_fields = ('service', 'cell', 'patient', )


class CellAdmin(admin.ModelAdmin):
    list_display = ('date', 'time_start', 'time_end', 'cabinet', 'specialist')
    list_filter = ('date', 'specialist')
    ordering = ('-date', 'specialist')
    raw_id_fields = ('performing_services',)
    autocomplete_lookup_fields = {
        'm2m': ['performing_services', ]
    }


class SlotRestrictionInline(admin.TabularInline):
    model = SlotRestriction
    extra = 1


class ServiceRestrictionInline(admin.TabularInline):
    raw_id_fields = ('service',)
    model = ServiceRestriction
    extra = 1


class SpecialistRestrictionInline(admin.TabularInline):
    model = SpecialistRestriction
    extra = 1


class ProfileSettingsAdmin(admin.ModelAdmin):
    inlines = [SlotRestrictionInline, ServiceRestrictionInline, SpecialistRestrictionInline, ]


class NumberOfServiceRestrictionAdmin(admin.ModelAdmin):
    raw_id_fields = ('service',)
    exclude = ('number_of_used',)


class SiteServicePermissoionAdmin(admin.ModelAdmin):
    list_display = ('site',)
    raw_id_fields = ('services',)
    autocomplete_lookup_fields = {
        'm2m': ['services', ]
    }


class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('site',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'users_str')
    form = UserProfileForm


class SlotTypeAdmin(admin.ModelAdmin):
    list_filter = ('clinic', )

admin.site.register(Service, ServiceAdmin)
admin.site.register(Specialist, SpecialistAdmin)
admin.site.register(Cell, CellAdmin)
admin.site.register(Cabinet, CabinetAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Clinic, ClinicAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Specialization, admin.ModelAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(NumberOfServiceRestriction, NumberOfServiceRestrictionAdmin)
admin.site.register(SlotType, SlotTypeAdmin)
admin.site.register(ProfileSettings, ProfileSettingsAdmin)
admin.site.register(SiteServiceRestriction, SiteServicePermissoionAdmin)
admin.site.register(SiteConfig, SiteConfigAdmin)

