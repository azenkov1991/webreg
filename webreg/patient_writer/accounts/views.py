import logging
from registration.views import RegistrationView, ActivationView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import login as DjangoLogin, logout as DjangoLogout
from django.http import HttpResponse
from main.logic import *
from patient_writer.accounts.forms import PatientRegistrationForm
from patient_writer.accounts.models import PatientRegistrationProfile

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
        return new_user

    def get_success_url(self, user):
        return self.success_url, (), {}


class PatientActivationView(ActivationView):

    def activate(self, request, activation_key):
        activated_user = PatientRegistrationProfile.objects.activate_user(activation_key)
        return activated_user

    def get_success_url(self, user):
        return reverse_lazy('patient_writer:activation_complete'), (), {}


def login(request, *args, **kwargs):
    http = DjangoLogin(request, *args, **kwargs)
    if request.GET:
        patient_id = request.session.get('patient_id', None)
        if patient_id:
            return redirect('patient_writer:input_second_step')

    if request.POST:
        try:
            user = request.user
            patient = Patient.objects.get(user_id=user.id)
            request.session['patient_id'] = patient.id
            request.session['clinic_id'] = patient.clinic.id
        except Patient.DoesNotExist:
            pass
    return http


def logout(request, *args, **kwargs):
    http = DjangoLogout(request, *args, **kwargs)
    try:
        del request.session['patient_id']
        del request.session['clinic_id']
    except KeyError:
        pass
    return http

