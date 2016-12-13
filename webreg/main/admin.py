from django.contrib import admin
from django import forms
from .models import *
from catalogs.models import OKMUService


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'clinic')


class DepartmentInline(admin.StackedInline):
    model = Department


class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address',)
    search_fields = ('name', 'address',)
    inlines = [DepartmentInline, ]


class PerformingServicesInline(admin.TabularInline):
    model = Specialist.performing_services.through
    extra = 1


class SpecialistAdmin(admin.ModelAdmin):
    list_display = (
        'fio', 'specialization', 'department',
    )
    list_display_links = ('fio', 'specialization')
    search_fields = ('fio', 'specialization')
    inlines = [PerformingServicesInline, ]


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
            self.fields['service'].queryset = OKMUService.objects.all()


class AppointmentAdmin(admin.ModelAdmin):
    form = AppointmentForm


class CellAdmin(admin.ModelAdmin):
    list_display = ('date', 'time_start', 'time_end', 'cabinet', 'specialist')
    list_filter = ('date', 'specialist')
    search_fields = ('specialist', 'date')
    ordering = ('-date', 'specialist')


class UserSlotRestrictionInline(admin.TabularInline):
    model = UserSlotRestriction
    extra = 1
    raw_id_fields = ('user_profile',)


class UserProfileAdmin(admin.ModelAdmin):
    inlines = [UserSlotRestrictionInline, ]


class NumberOfServiceRestrictionAdmin(admin.ModelAdmin):
    exclude = ('number_of_used',)

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
admin.site.register(SlotType, admin.ModelAdmin)

