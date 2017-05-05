import datetime
from xhtml2pdf import pisa
import io
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import StreamingHttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, View
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from patient_writer.forms import InputFirstStepForm
from patient_writer.models import DepartmentConfig, ClinicConfig, SpecializationConfig
from main.mixins import ProfileRequiredMixin
from main.logic import *
from .logic import get_allowed_slot_types, get_specialist_service


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


class PatientWriteSecondStep(ProfileRequiredMixin, TemplateView):
    template_name = 'patient_writer/input_second_step.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        clinic_id = request.session.get('clinic_id', None)
        patient_id = request.session.get('patient_id', None)
        if not clinic_id or not patient_id:
            return redirect("patient_writer:input_first_step")
        years_old = Patient.objects.get(id=patient_id).age
        departments = Department.objects.filter(
            clinic_id=clinic_id,
            departmentconfig__min_age__lte=years_old,
            departmentconfig__max_age__gte=years_old)
        context['departments'] = departments
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        try:
            speciality_id = request.POST['speciality']
            specialist_id = request.POST['specialist']
            department_id = request.POST['department']
            cell_id = request.POST['cell']
            patient_id = request.session['patient_id']
        except KeyError:
            redirect('patient_writer:input_second_step')
        user_profile = request.user_profile
        cell = Cell.objects.get(id=cell_id)
        specialist = Specialist.objects.get(id=specialist_id)
        patient = Patient.objects.get(id=patient_id)
        department = Department.objects.get(id=department_id)
        allowed_slot_types = get_allowed_slot_types(user_profile, patient, department, specialist.specialization)
        if cell.slot_type.id not in allowed_slot_types:
            raise PermissionDenied
        service = get_specialist_service(specialist)
        # Для специализации и специалиста обязательно должна быть настроена услуга
        if not service:
            raise PermissionDenied
        request.session['cell_id'] = cell_id
        if request.session.get('error', None):
            del request.session['error']
        try:
            appointment = create_appointment(
                user_profile, patient, specialist, service, cell.date, cell
            )
            request.session['appointment_id'] = appointment.id
        except AppointmentError as e:
            request.session['error'] = str(e)
            log.error(str(e))
        return redirect("patient_writer:talon")


class TalonView(ProfileRequiredMixin, TemplateView):
    template_name = 'patient_writer/talon.html'

    def get(self, request, *args, **kwargs):
        try:
            appointment_id = request.session['appointment_id']
        except KeyError:
            redirect("patient_writer:input_second_step")
        context = self.get_context_data(**kwargs)
        try:
            cell = Cell.objects.get(id=request.session['cell_id'])
        except Exception as e:
            context['error'] = str(e)
        context['error'] = request.session.get('error', None)
        context['cell'] = cell
        context['appointment_id'] = appointment_id
        return self.render_to_response(context)


class TalonPdf(ProfileRequiredMixin, View):
    def get(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if request.session['patient_id'] != appointment.patient.id:
                raise PermissionDenied
        except Appointment.DoesNotExist:
            raise PermissionDenied
        cell = appointment.cell
        department = cell.specialist.department

        try:
            clinic_conf = department.clinic.clinicconfig
            phone = clinic_conf.phone
            phone2 = clinic_conf.phone2
            logo = clinic_conf.logo.path if clinic_conf.logo else ''
        except ClinicConfig.DoesNotExist:
            phone = None
            phone2 = None
            logo = ''

        try:
            dep_conf = department.departmentconfig
            phone = dep_conf.phone if dep_conf.phone else phone
            phone2 = dep_conf.phone2 if dep_conf.phone2 else phone2
            try:
                spec_conf = SpecializationConfig.objects.get(
                    department_config=dep_conf,
                    specialization=cell.specialist.specialization
                )
                comment = spec_conf.comment if spec_conf.is_show_comment else None
            except SpecializationConfig.DoesNotExist:
                comment = None
        except DepartmentConfig.DoesNotExist:
            comment = None

        context = {
            'departament_name': department.name,
            'departament_address': department.address,
            'date_episode': cell.date.strftime('%d-%m-%Y'),
            'time_episode': cell.time_start.strftime('%H:%M'),
            'cabinet': cell.cabinet.name if appointment.cell.cabinet else '',
            'doctor': cell.specialist.fio,
            'phone_cancel': phone,
            'phone': phone2,
            'create_episode_date': appointment.created_time.astimezone(tz=None).strftime('%d-%m-%Y   %H:%M'),
            'speciality_comment': comment,

            'logo': logo,
            'fio': appointment.patient.fio,
            'faq': '',
        }
        result = io.BytesIO()
        html = render_to_string('patient_writer/talon_pdf.html', context)
        pdf = pisa.pisaDocument(html, result, encoding='UTF-8')
        if not pdf.err:
            wrapper = FileWrapper(result)
            response = StreamingHttpResponse(wrapper, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=talon_{0}.pdf'.format(
                    appointment.id
            )
            response['Content-Length'] = result.tell()
            result.seek(0)
        return response


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

        # для исключения ячеек котрые попадают в защитный интервал дня
        today = datetime.datetime.today()
        time_before = (today + datetime.timedelta(minutes=department.departmentconfig.today_time_interval)).time()

        # Получение всех ячеек специалиста за этот период
        cells = Cell.get_free_cells(specialist, date_from, date_to).filter(slot_type__in=allowed_slot_types).\
            exclude(date=today.date(), time_start__lte=time_before)

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
                    cell = cells.get(date=date, time_start=time)
                    color = cell.slot_type.color
                    text = time.strftime("%H:%M")
                    id = cell.id
                except Cell.DoesNotExist:
                    color = "gray"
                    text = ""
                    id = ""
                # if cells.filter(date=date, time_start=time).exists():
                #     color = "#9adacd"
                #     text = time.strftime("%H:%M")
                # else:
                #     color = "gray"
                #     text = ""
                times.append({
                    "text": text,
                    "color": color,
                    "id": id,
                    "time": time,
                    "date": date
                })
            dates.append({
                'date': date,
                'times': times
            })
        context['dates'] = dates
        context['timetable_header'] = "Выберите время"

        return self.render_to_response(context)


class HelpView(TemplateView):
    template_name = 'patient_writer/help.html'
