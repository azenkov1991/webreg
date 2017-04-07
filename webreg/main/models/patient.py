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
    polis_number = models.CharField(
        max_length=16,
        verbose_name="Номер полиса",
        null=True
    )
    polis_seria = models.CharField(
        max_length=6, verbose_name="Серия полиса",
        null=True, blank=True
    )
    clinic = models.ManyToManyField(
        'main.Clinic', verbose_name="Мед. учреждение"
    )

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