from django.shortcuts import render
from django.views.generic import FormView
from django.contrib.auth import login
from patient_writer.forms import InputFirstStepForm, InputSecondStepForm

class PatientWriteFirstStep(FormView):
    template_name = 'patient_writer/input_first_step.html'
    form_class = InputFirstStepForm
    success_url = '/pwriter/input_second_step'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            login(request, form.get_user())
        return super(PatientWriteFirstStep, self).post(request, *args, **kwargs)

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
