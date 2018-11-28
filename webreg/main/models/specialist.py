from django.db import models
from mixins.models import SafeDeleteMixin


class Specialist(SafeDeleteMixin):
    fio = models.CharField(
        max_length=128, verbose_name="Полное имя"
    )
    specialization = models.ForeignKey(
        'main.Specialization', verbose_name="Специализация",
        null=True, on_delete=models.SET_NULL
    )
    performing_services = models.ManyToManyField(
        "main.Service", verbose_name="Выполняемые услуги"
    )
    department = models.ForeignKey(
        'main.Department', verbose_name="Подразделение"
    )

    def __str__(self):
        return self.fio

    class Meta:
        app_label = 'main'
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"
