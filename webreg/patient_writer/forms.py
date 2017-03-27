from django import forms
from django.contrib.auth import authenticate
from django.conf import settings
from datetime import date
from constance import config
from main.validators import oms_polis_number_validation
from main.models import Clinic, PatientError
from main.logic import find_patient_by_polis_number


class InputFirstStepForm(forms.Form):
    city = forms.ChoiceField(
        choices=list(Clinic.objects.order_by('-city').values_list('city','city').distinct()),
        label='Город',
        widget=forms.Select()
    )
    polis_number = forms.CharField(
        max_length=16, label='Номер полиса',
        widget=forms.TextInput(attrs={
            'class': 'form__unit-item-input form__unit-item-input-line',
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
            'class': 'form__unit-item-input form__unit-item-input-line',
            'placeholder': 'оставьте пустым для полиса нового образца',
            'autocomplete': 'off',
        }),
        help_text='Пример: КМС'
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        widget=forms.DateInput(attrs={
            'autocomplete': 'off',
            'placeholder': 'дд.мм.гггг',
        }),
    )
    phone = forms.CharField(
        max_length=20, label='Сотовый телефон',
        widget=forms.TextInput(attrs={
            'class': 'mobile-phone-input',
            'placeholder': 'сотовый/домашний в формате +7 (XXX) XXX-XX-XX',
            'autocomplete': 'off',
        }),
        help_text='Пример: +7 (XXX) XXX-XX-XX'
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
        if not phone.startswith('+7'):
            raise forms.ValidationError('Телефон должен начинаться на +7')
        elif len(phone) != 18:
            raise forms.ValidationError('Неверный формат телефона')
        return phone.translate({ord('('):None,
                               ord(')'):None,
                               ord('-'):None,
                               ord(' '): None})

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date <= date(year=1900, month=12, day=31):
            raise ValidationError('Некорректная дата')
        else:
            return birth_date


    def clean(self):
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
        try:
            patient = find_patient_by_polis_number(clinic, polis_number, birth_date, polis_seria)
        except PatientError as er:
            raise forms.ValidationError(str(er))

        if not patient:
            raise forms.ValidationError(
                config.PBSEARCH_ERROR,
            )
        self.user = authenticate(username=settings.PATIENT_WRITER_USER)
        if self.user is None:
            raise forms.ValidationError(
                "Мед учреждение",
                code='invalid_login',
                params={'username': self.username_field.verbose_name},
            )

        self.cleaned_data['user_id'] = self.user.id
        self.cleaned_data['patient_id'] = patient.id
        return self.cleaned_data

    def get_user(self):
        return self.user

class InputSecondStepForm(forms.Form):
    pass
