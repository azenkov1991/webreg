from constance import config
from django import forms
from django.utils.html import format_html
from registration.forms import RegistrationFormUniqueEmail
from main.logic import *

from main.validators import oms_polis_number_validation, birth_date_validation, mobile_phone_validation

# ----------------------------------------------------------------------------------------------------------------------
# CheckBox соглашение
# ----------------------------------------------------------------------------------------------------------------------


class CheckBoxAgree(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        out_html = super(CheckBoxAgree, self).render(name, value, attrs)
        return format_html('<label class="checkbox">{0}<span class="checkbox">Я принимаю \
                    <a href="{1}">правила обработки даных</a> \
                    ФГБУ ФСНКЦ ФМБА России</span></label>', out_html, "/pwriter/agreement")


class PatientRegistrationForm(RegistrationFormUniqueEmail):
    def __init__(self, *args, **kwargs):
        super(PatientRegistrationForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['username', 'email', 'description']

    try:
        city_choices = list(Clinic.objects.order_by('-city').values_list('city', 'city').distinct())
    except:
        city_choices = []
    city = forms.ChoiceField(
        choices=city_choices,
        label='Город',
        widget=forms.Select()
    )
    polis_number = forms.CharField(
        max_length=16, label='Номер полиса',
        widget=forms.TextInput(
            attrs={
                'placeholder': '16 знаков!',
                'mask': '9999999999999999',
                'mask-restrict': 'reject',
            }
        ),
        help_text='Пример: 2450000011112222',
        validators=[oms_polis_number_validation, ]
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(
            attrs={
                'class': 'dateinput',
                'autocomplete': 'off',
                'placeholder': 'дд.мм.гггг'
            }
        ),
        help_text='Пример: 01.01.2001',
        validators=[birth_date_validation, ]
    )
    phone = forms.CharField(
        max_length=20, label='Сотовый телефон',
        widget=forms.TextInput(
            attrs={
                'class': 'mobile-phone-input',
                'placeholder': '+7 (XXX) XXX-XX-XX',
                'autocomplete': 'off',
            }
        ),
        help_text='Пример: +7 (999) 888-77-66',
        validators=[mobile_phone_validation, ]
    )
    agree = forms.BooleanField(
        label='Подтверждение',
        widget=CheckBoxAgree(attrs={'class': 'checkbox__input', 'id': 'confirm'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RegistrationFormUniqueEmail, self).__init__(*args, **kwargs)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        return phone.translate({ord('('): None,
                                ord(')'): None,
                                ord('-'): None,
                                ord(' '): None})

    def clean(self):
        super(PatientRegistrationForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        request_param = map(lambda u: cleaned_data.get(u), ('city', 'polis_number', 'polis_seria', 'birth_date'))
        city, polis_number, polis_seria, birth_date = request_param
        clinic = Clinic.objects.filter(city=city).first()

        if not clinic:
            raise forms.ValidationError(
                "Не найдено Мед. учреждение для этого города",
            )
        self.cleaned_data['clinic_id'] = clinic.id
        try:
            patient = find_patient_by_polis_number(clinic, polis_number, birth_date, polis_seria)
            self.cleaned_data['patient_id'] = patient.id
        except PatientError as er:
            raise forms.ValidationError(str(er))

        if not patient:
            raise forms.ValidationError(
                config.PBSEARCH_ERROR,
            )
        return self.cleaned_data



