import datetime
from xhtml2pdf import pisa
import io
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import StreamingHttpResponse, HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, View, ListView, DetailView, DeleteView
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib.auth.views import login as DjangoLogin, logout as DjangoLogout
from patient_writer.forms import InputFirstStepForm
from patient_writer.models import DepartmentConfig, ClinicConfig, SpecializationConfig
from main.mixins import ProfileRequiredMixin
from main.logic import *
from patient_writer.logic import get_allowed_slot_types, get_specialist_service
from loghandle.models import UserAction as action


class Actions:
    AUTHENTICATION = 'Аутентификация'
    CONFIRM = 'Подтверждение пользователя'
    GET_DEPARTMENTS = 'Получение списка подразделений'
    GET_SPECIALITIES = 'Получение специальностей'
    GET_SPECIALISTS = 'Получение специалистов'
    GET_TIMETABLE = 'Получение расписания'
    CHECK_FREE_CELL = 'Проверка доступности ячейки'
    CREATE_APPOINTMENT = 'Создание назначения'
    GET_TALON = 'Получение талона'
    CANCEL_APPOINTMENT = 'Отмена записи'
    REGISTER = "Пользователь зарегистрировался"
    ACTIVE = "Пользователь стал активным"
    LOGIN = "Пользоваетль залогинился"
    LOGOUT = "Пользователь вышел"
    WRONG_PASSWORD = "Неверный пароль"


class PatientWriteFirstStep(FormView):
    template_name = 'infomat_writer/input_first_step.html'
    form_class = InputFirstStepForm
    success_url = reverse_lazy('infomat_writer:confirm')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            login(request, form.get_user(), backend='main.authentication.PolisNumberBackend')

            # сохранение id пациента в сессии для последующих шагов
            request.session['patient_id'] = form.cleaned_data['patient_id']
            request.session['phone'] = form.cleaned_data['phone']
            action.log(Actions.AUTHENTICATION)

        return super(PatientWriteFirstStep, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        request.session.flush()
        department_id = int(kwargs['department'])
        request.session['department_id'] = department_id
        print(department_id)
        try:
            department = Department.objects.get(id=department_id)
            request.session['clinic_id'] = department.clinic.id
        except Department.DoesNotExist:
            raise Http404
        return super(PatientWriteFirstStep, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({'department_id': self.request.session['department_id']})
        return super(PatientWriteFirstStep, self).get_context_data(**kwargs)


class Confirm(TemplateView):
    template_name = 'infomat_writer/confirm.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        patient_id = request.session.get('patient_id', None)
        clinic_id = request.session.get('clinic_id', None)
        if not patient_id or not clinic_id:
            return redirect('infomat_writer:input_first_step', department=request.session['department_id'])
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return redirect('infomat_writer:input_first_step', department=request.session['department_id'])
        return self.render_to_response(context)


class PatientWriteSecondStep(ProfileRequiredMixin, TemplateView):
    template_name = 'infomat_writer/input_second_step.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        patient_id = request.session.get('patient_id', None)
        try:
            patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            return HttpResponse(status=500)
        # обновление телефона пациента
        phone = request.session.get('phone', None)
        if phone:
            update_patient_phone_number(patient, phone)
        if not patient_id:
            return redirect("infomat_writer:input_first_step", department=self.request.session['department_id'])
        action.log(Actions.CONFIRM)
        years_old = patient.age
        clinic_id = self.request.session['clinic_id']
        try:
            clinic = Clinic.objects.get(id=clinic_id)
        except Clinic.DoesNotExist:
            return redirect('infomat_writer:input_first_step', department=self.request.session['department_id'])

        departments = Department.objects.filter(
            clinic_id=clinic.id,
            departmentconfig__min_age__lte=years_old,
            departmentconfig__max_age__gte=years_old
        ).order_by('departmentconfig__order')
        context['departments'] = departments
        context['department_id'] = request.session.get('department_id', None)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        try:
            speciality_id = request.POST['speciality']
            specialist_id = request.POST['specialist']
            department_id = request.session['department_id']
            cell_id = request.POST['cell']
            patient_id = request.session['patient_id']
        except KeyError:
            redirect('infomat_writer:input_second_step')
        user_profile = request.user_profile
        cell = Cell.objects.get(id=cell_id)
        specialist = Specialist.objects.get(id=specialist_id)
        patient = Patient.objects.get(id=patient_id)
        department = Department.objects.get(id=department_id)
        allowed_slot_types = get_allowed_slot_types(user_profile, patient, department, specialist.specialization)
        if cell.slot_type.id not in allowed_slot_types:
            raise PermissionDenied("Нет доступных для назначения слотов")
        service = get_specialist_service(specialist)
        # Для специализации и специалиста обязательно должна быть настроена услуга
        if not service:
            raise ImproperlyConfigured("Для специализации и специалиста обязательно должна быть настроена услуга")
        request.session['cell_id'] = cell_id
        if request.session.get('error', None):
            del request.session['error']
        try:
            appointment = create_appointment(
                user_profile, patient, specialist, service, cell.date, cell
            )
            action.log(Actions.CREATE_APPOINTMENT)
            request.session['appointment_id'] = appointment.id
            appointment.send_sms()
        except AppointmentError as e:
            request.session['error'] = str(e)
            log.error(str(e))
        return redirect("infomat_writer:talon")


class TalonView(ProfileRequiredMixin, TemplateView):
    template_name = 'infomat_writer/talon.html'

    def get(self, request, *args, **kwargs):
        appointment_id = request.session.get('appointment_id', None)
        context = self.get_context_data(**kwargs)
        try:
            cell = Cell.objects.get(id=request.session['cell_id'])
        except Exception as e:
            context['error'] = str(e)
        context['error'] = request.session.get('error', None)
        context['cell'] = cell
        context['appointment_id'] = appointment_id
        return self.render_to_response(context)


def logout(request, *args, **kwargs):
    kwargs.update(
        {
            'next_page': '/infomat_writer/input_first_step/' + str(request.session['department_id']) + '/'
        },
    )
    action.log(Actions.LOGOUT)
    http = DjangoLogout(request, *args, **kwargs)
    try:
        del request.session['patient_id']
        del request.session['clinic_id']
    except KeyError:
        pass
    return http


