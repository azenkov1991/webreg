import logging
from registration.views import RegistrationView, ActivationView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import login as DjangoLogin, logout as DjangoLogout
from django.http import HttpResponse
from django.views.generic import TemplateView
from main.logic import *
from patient_writer.accounts.forms import PatientRegistrationForm
from patient_writer.accounts.models import PatientRegistrationProfile
from loghandle.models import UserAction as action


class Actions:
    REGISTER = "Пользователь зарегистрировался"
    ACTIVE = "Пользователь стал активным"
    LOGIN = "Пользоваетль залогинился"
    LOGOUT = "Пользователь вышел"
    WRONG_PASSWORD = "Неверный пароль"

log = logging.getLogger("webreg")


class PatientRegistrationView(RegistrationView):
    disallowed_url = reverse_lazy('patient_writer:registration_disallowed')
    template_name = 'patient_writer/accounts/register.html',
    form_class = PatientRegistrationForm,
    success_url = reverse_lazy('patient_writer:registration_complete')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.site = get_current_site(request)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def register(self, form):
        site = self.site
        new_user = PatientRegistrationProfile.objects.create_inactive_user(form, site)
        cleaned_data = form.cleaned_data
        try:
            profile = UserProfile.objects.get(name=settings.PATIENT_WRITER_PROFILE)
            profile.user.add(new_user)
            try:
                patient = Patient.objects.get(pk=cleaned_data['patient_id'])
                try:
                    update_patient_phone_number(patient, cleaned_data['phone'])
                except PatientError as er:
                    log.error("Ошибка при обновлении телефона" + str(er) + str(cleaned_data))
                    return HttpResponse(status=500)
                patient.user = new_user
                patient.save()
                try:
                    clinic = Clinic.objects.get(pk=cleaned_data['clinic_id'])
                    patient.clinic = clinic
                except Clinic.DoesNotExist:
                    log.error("Ошибка при регистрации. Не найден пациент не найдено мед. учреждение"
                              + str(cleaned_data))
            except Patient.DoesNotExist:
                log.error("Ошибка при регистрации. Не найден пациент" + str(cleaned_data))
                return HttpResponse(status=500)
        except UserProfile.DoesNotExist:
            raise ImproperlyConfigured("Необходимо настроить профиль пользователя для записи на прием")
        new_user.save()
        action.log(Actions.REGISTER, user_id=new_user.id)
        return new_user

    def get_success_url(self, user):
        return self.success_url, (), {}


class PatientActivationView(ActivationView):

    def activate(self, request, activation_key):
        activated_user = PatientRegistrationProfile.objects.activate_user(activation_key)
        if activated_user:
            action.log(Actions.ACTIVE, user_id=activated_user.id)
        return activated_user

    def get_success_url(self, user):
        return reverse_lazy('patient_writer:activation_complete'), (), {}


def login(request, *args, **kwargs):
    http = DjangoLogin(request, *args, **kwargs)
    if request.method == 'GET':
        patient_id = request.session.get('patient_id', None)
        if patient_id:
            return redirect('patient_writer:input_second_step')

    if request.method == 'POST':
        try:
            user = request.user
            if user.id:
                patient = Patient.objects.get(user_id=user.id)
                request.session['patient_id'] = patient.id
                request.session['clinic_id'] = patient.clinic.id
        except Patient.DoesNotExist:
            pass
        if user.id:
            action.log(Actions.LOGIN)
        else:
            action.log(
                Actions.WRONG_PASSWORD,
                info={
                    'username': http.context_data['form'].cleaned_data['username'],
                    'password': http.context_data['form'].cleaned_data['password'],
                }
            )

    return http


class LogOutConfirmView(TemplateView):
    template_name = 'patient_writer/accounts/logout.html'


def logout(request, *args, **kwargs):
    kwargs.update({'next_page': 'patient_writer:input_first_step'})
    action.log(Actions.LOGOUT)
    http = DjangoLogout(request, *args, **kwargs)
    try:
        del request.session['patient_id']
        del request.session['clinic_id']
    except KeyError:
        pass
    return http

