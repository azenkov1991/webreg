from django import forms
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.html import format_html
from datetime import date
from constance import config
from main.validators import oms_polis_number_validation, birth_date_validation, mobile_phone_validation
from main.models import Clinic, PatientError
from main.logic import find_patient_by_polis_number

BIRTH_YEAR_CHOICES = [year for year in range(date.today().year, date.today().year-120, -1)]


class InputFirstStepForm(forms.Form):
    polis_number = forms.CharField(
        max_length=16, label='Номер полиса',
        widget=forms.TextInput(attrs={
            'placeholder': '16 знаков для полиса нового образца',
            'autocomplete': 'off',
            'mask': '9999999999999999',
            'mask-restrict': 'reject',
        }),
        help_text='Пример: 2450000011112222',
        validators=[oms_polis_number_validation,]
    )
    polis_seria = forms.CharField(
        max_length=6, label='Серия полиса', required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'оставьте пустым для полиса нового образца',
            'autocomplete': 'off',
            'disabled': 'disabled',
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
        validators=[birth_date_validation, ]
    )
    phone = forms.CharField(
        max_length=20, label='Сотовый телефон',
        widget=forms.TextInput(attrs={
            'class': 'mobile-phone-input',
            'placeholder': 'сотовый/домашний в формате +7 (XXX) XXX-XX-XX',
            'autocomplete': 'off',
        }),
        help_text='Пример: +7 (XXX) XXX-XX-XX',
        validators=[mobile_phone_validation, ]
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = None
        super(InputFirstStepForm, self).__init__(*args, **kwargs)

    def clean_polis_seria(self):
        polis_seria = self.cleaned_data['polis_seria']
        if 'polis_number' in self.cleaned_data:
            polis_number = self.cleaned_data['polis_number']
            if len(polis_number) == 7 and not len(polis_seria):
                raise forms.ValidationError('Необходима серия полиса')
        return polis_seria

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        return phone.translate({ord('('): None,
                               ord(')'): None,
                               ord('-'): None,
                               ord(' '): None})

    def clean(self):
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        request_param = map(lambda u: cleaned_data.get(u), ('city', 'polis_number', 'polis_seria', 'birth_date'))
        city, polis_number, polis_seria, birth_date = request_param

        try:
            patient = find_patient_by_polis_number(polis_number, birth_date, polis_seria)
        except PatientError as er:
            raise forms.ValidationError(str(er))

        if not patient:
            raise forms.ValidationError(
                config.PBSEARCH_ERROR,
            )

        if not patient.user:
            self.user = authenticate(username=settings.PATIENT_WRITER_USER)
        else:
            self.user = authenticate(
                username=patient.user.username, polis_number=patient.polis_number,
                birth_date=patient.birth_date,
                polis_seria=patient.polis_seria
            )

        if self.user is None:
            raise forms.ValidationError(
                "Мед учреждение",
                code='invalid_login',
                params={'username': self.username_field.verbose_name},
            )
        self.cleaned_data['clinic_id'] = patient.clinic.id
        self.cleaned_data['user_id'] = self.user.id
        self.cleaned_data['patient_id'] = patient.id
        return self.cleaned_data

    def get_user(self):
        return self.user


class InputSecondStepForm(forms.Form):
    pass


class RegistrationForm(forms.Form):
    pass
