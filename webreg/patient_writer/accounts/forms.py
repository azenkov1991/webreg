from datetime import date
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


BIRTH_YEAR_CHOICES = [year for year in range(date.today().year, date.today().year-120, -1)]


class PatientRegistrationForm(RegistrationFormUniqueEmail):
    def __init__(self, *args, **kwargs):
        super(PatientRegistrationForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['username', 'email', 'description']

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
    polis_seria = forms.CharField(
        max_length=6, label='Серия полиса', required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'оставьте пустым для полиса нового образца',
            'autocomplete': 'off',
        }),
        help_text='Пример: КМС'
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.SelectDateWidget(
            years=BIRTH_YEAR_CHOICES,
            attrs={
                'autocomplete': 'off',
                'placeholder': 'дд.мм.гггг',
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
    def clean_polis_seria(self):
        polis_seria = self.cleaned_data['polis_seria']
        if 'polis_number' in self.cleaned_data:
            polis_number = self.cleaned_data['polis_number']
            if len(polis_number) == 7 and not len(polis_seria):
                raise forms.ValidationError('Необходима серия полиса')
        return polis_seria

    def clean(self):
        super(PatientRegistrationForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        request_param = map(lambda u: cleaned_data.get(u), ('city', 'polis_number', 'polis_seria', 'birth_date'))
        city, polis_number, polis_seria, birth_date = request_param


        try:
            patient = find_patient_by_polis_number(polis_number, birth_date, polis_seria)
            if not patient:
                raise forms.ValidationError(
                    config.PBSEARCH_ERROR,
            )
            self.cleaned_data['patient_id'] = patient.id
            self.cleaned_data['clinic_id'] = patient.clinic.id
        except PatientError as er:
            raise forms.ValidationError(str(er))


        return self.cleaned_data



