from django.db import models
from catalogs.models import OKMUService


class Clinic(models.Model):
    name = models.CharField(max_length=128, verbose_name="Наименование мед. учреждения")
    city = models.CharField(max_length=128, verbose_name="Город")
    address = models.CharField(max_length=256, verbose_name="Адрес")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Мед. уреждение"
        verbose_name_plural = "Мед. учреждения"


class Department(models.Model):
    name = models.CharField(max_length=128, verbose_name="Название подразделения")
    parent_department = models.ForeignKey('self', blank=True, null=True)
    clinic = models.ForeignKey(Clinic, verbose_name="Мед. учреждение")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ""
        verbose_name_plural = "Мед. учреждения"


class Specialist(models.Model):
    fio = models.CharField(max_length=128, verbose_name="Полное имя")
    specialization = models.CharField(max_length=128, verbose_name='Специализация', blank=True, null=True)
    performing_services = models.ManyToManyField(OKMUService, verbose_name="Выполняемые услуги")
    department = models.ForeignKey(Department, verbose_name="Подразделение")

    def __str__(self):
        return self.fio

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"


class Cabinet(models.Model):
    number = models.PositiveIntegerField(verbose_name="Номер кабинета", unique=True)
    name = models.CharField(max_length=128, verbose_name="Название")
    department = models.ForeignKey(Department, verbose_name="Подразделение")

    def __str__(self):
        return "Кабинет " + str(self.number)

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"








