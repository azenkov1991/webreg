from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView
from django.contrib.auth import login
from patient_writer.forms import InputFirstStepForm, InputSecondStepForm
from main.models import Patient

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
        return super(PatientWriteFirstStep, self).post(request, *args, **kwargs)

class Confirm(TemplateView):
    template_name = 'patient_writer/confirm.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        patient_id = request.session.get('patient_id',None)
        if not patient_id:
            return redirect("patient_writer:input_first_step")
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return redirect("patient_writer:input_first_step")
        context['patient'] = patient
        return self.render_to_response(context)


class PatientWriteSecondStep(FormView):
    template_name = 'patient_writer/input_second_step.html'
    form_class = InputSecondStepForm
    success_url = '/pwriter/input_third_step'



    # ----------------------------------------------------------------------------
    # начальная загрузка формы ввода данных для поиска пациента
    # ----------------------------------------------------------------------------
    # def get(self, request, *args, **kwargs):
    #     pass

    # ----------------------------------------------------------------------------
    # проверка данных формы
    # ----------------------------------------------------------------------------
    # def post(self, request, *args, **kwargs):
    #     pass

    # ----------------------------------------------------------------------------
    # Контекстные данные
    # ----------------------------------------------------------------------------
    # def get_context_data(self, **kwargs):
    #     kwargs['city'] = Clinic.objects.order_by().values_list('city', flat=True)
    #     return super(PatientWriteFistStep,self)
