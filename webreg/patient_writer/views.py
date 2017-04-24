import datetime
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView
from django.contrib.auth import login
from patient_writer.forms import InputFirstStepForm, InputSecondStepForm
from main.mixins import ProfileRequiredMixin
from main.logic import *
from .logic import get_allowed_slot_types


class PatientWriteFirstStep(FormView):
    template_name = 'patient_writer/input_first_step.html'
    form_class = InputFirstStepForm
    success_url = '/pwriter/confirm'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            login(request, form.get_user())
            # сохранение id пациента в сессии для последующих шагов
            request.session['patient_id'] = form.cleaned_data['patient_id']
            request.session['clinic_id'] = form.cleaned_data['clinic_id']
        return super(PatientWriteFirstStep, self).post(request, *args, **kwargs)


class Confirm(TemplateView):
    template_name = 'patient_writer/confirm.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        patient_id = request.session.get('patient_id', None)
        clinic_id = request.session.get('clinic_id', None)
        if not patient_id or not clinic_id:
            return redirect("patient_writer:input_first_step")
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return redirect("patient_writer:input_first_step")
        context['patient'] = patient
        return self.render_to_response(context)


class PatientWriteSecondStep(TemplateView):
    template_name = 'patient_writer/input_second_step.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        clinic_id = request.session.get('clinic_id', None)
        patient_id = request.session.get('patient_id' , None)
        if not clinic_id or not patient_id:
            return redirect("patient_writer:input_first_step")
        years_old = Patient.objects.get(id=patient_id).age
        departments = Department.objects.filter(
            clinic_id=clinic_id,
            departmentconfig__min_age__lte=years_old,
            departmentconfig__max_age__gte=years_old)
        context['departments'] = departments
        return self.render_to_response(context)


class SpecialistTimeTable(ProfileRequiredMixin, TemplateView):
    template_name = "timetable/specialist_row.html"

    def get(self, request, specialist_id, **kwargs):
        try:
            patient_id = request.session['patient_id']
            patient = Patient.objects.get(id=patient_id)
        except Exception as e:
            return redirect("patient_writer:input_first_step")

        user_profile = request.user_profile
        context = self.get_context_data(**kwargs)
        try:
            specialist = Specialist.objects.get(pk=specialist_id)
        except Specialist.DoesNotExist:
            return self.render_to_response({})
        department = specialist.department
        # Определение периода за который берем расписание из настроек отделения
        date_from, date_to = department.departmentconfig.get_date_range()
        # Доступные слоты для отделения
        allowed_slot_types = get_allowed_slot_types(user_profile, patient, department, specialist.specialization)
        # Получение всех ячеек специалиста за этот период
        cells = Cell.get_free_cells(specialist, date_from, date_to).filter(slot_type__in=allowed_slot_types)
        # Формирование массива всех времен
        times_set = set()
        dates_set = set()
        for cell in cells:
            times_set.add(cell.time_start)
            dates_set.add(cell.date)
        times_list = sorted(times_set)
        dates_list = sorted(dates_set)
        dates = []
        for date in dates_list:
            times = []
            for time in times_list:
                try:
                    color = cells.get(date=date, time_start=time).slot_type.color
                    text = time.strftime("%H:%M")
                except Cell.DoesNotExist:
                    color = "gray"
                    text = ""
                # if cells.filter(date=date, time_start=time).exists():
                #     color = "#9adacd"
                #     text = time.strftime("%H:%M")
                # else:
                #     color = "gray"
                #     text = ""
                times.append({
                    "text": text,
                    "color": color
                })
            dates.append({
                'date': date,
                'times': times
            })
        context['dates'] = dates
        context['timetable_header'] = "Выберите время"

        return self.render_to_response(context)
