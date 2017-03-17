from django.shortcuts import render
from django.views.generic import FormView
class PatientWriteFistStep(FormView):
    template_name = 'patient_writer/input_first_step.html'
    form_class = InputInitialDataForm
    success_url = '/pwriter_writer/input_second_step.html'

    def get_form_kwargs(self):
        kwargs = super(PWriterInputInitialData, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    # ----------------------------------------------------------------------------
    # начальная загрузка формы ввода данных для поиска пациента
    # ----------------------------------------------------------------------------
    def get(self, request, *args, **kwargs):
        pass

    # ----------------------------------------------------------------------------
    # проверка данных формы
    # ----------------------------------------------------------------------------
    def post(self, request, *args, **kwargs):
        pass

    # ----------------------------------------------------------------------------
    # Контекстные данные
    # ----------------------------------------------------------------------------
    def get_context_data(self, **kwargs):
        # TODO: выбрать все города в контекст
