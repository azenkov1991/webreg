from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView
from django.contrib.auth import login
from patient_writer.forms import InputFirstStepForm, InputSecondStepForm
from main.models import Patient, Department

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
        if not clinic_id:
            return redirect("patient_writer:input_first_step")
        departments = Department.objects.filter(clinic_id=clinic_id)
        context['departments'] = departments
        return self.render_to_response(context)
