from datetime import date
from django.db import models
from main.validators import oms_polis_number_validation, birth_date_validation


class Patient(models.Model):
    first_name = models.CharField(
        max_length=128, verbose_name="Фамилия"
    )
    last_name = models.CharField(
        max_length=128, verbose_name="Имя"
    )
    middle_name = models.CharField(
        max_length=128, verbose_name="Отчество"
    )
    birth_date = models.DateField(
        verbose_name="Дата рождения",
        validators=[birth_date_validation,]
    )
    phone = models.CharField(
        max_length=31, verbose_name="Телефон",
        blank=True, null=True
    )
    polis_number = models.CharField(
        max_length=16,
        verbose_name="Номер полиса",
        null=True
    )
    polis_seria = models.CharField(
        max_length=6, verbose_name="Серия полиса",
        blank=True, null=True
    )
    clinics = models.ManyToManyField(
        'main.Clinic', verbose_name="Мед. учреждения",
        related_name="patients"
    )
    clinic_attached = models.ForeignKey(
        'main.Clinic', verbose_name='Мед. учреждение прикреплкния',
        related_name='attached_patients',
        null=True, blank=True
    )
    user = models.ForeignKey(
        'auth.User',
        verbose_name="Пользователь",
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - \
            ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def fio(self):
        return self.first_name + " " + self.last_name + " " + self.middle_name

    def __str__(self):
        return self.first_name + " " + self.last_name[0] + ". " + \
               self.middle_name[0] + "., " + self.birth_date.strftime("%d.%m.%Y")

    def full_clean(self, exclude=None, validate_unique=True):
        if not self.polis_seria:
             oms_polis_number_validation(self.polis_number)
        super(Patient,self).full_clean(exclude,validate_unique)

    class Meta:
        app_label = 'main'
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"
