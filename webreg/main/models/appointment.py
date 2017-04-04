from django.db import models
from django.contrib.postgres.fields import JSONField
from mixins.models import TimeStampedModel, SafeDeleteMixin


class Appointment(TimeStampedModel, SafeDeleteMixin):
    user_profile = models.ForeignKey(
        'main.UserProfile', verbose_name="Профиль пользователя"
    )
    date = models.DateField(
        verbose_name="Дата приема", db_index=True
    )
    specialist = models.ForeignKey(
        'main.Specialist', verbose_name="Специалист"
    )
    service = models.ForeignKey(
        "catalogs.OKMUService", verbose_name="Услуга"
    )
    patient = models.ForeignKey(
        'main.Patient', verbose_name="Пациент"
    )
    cell = models.ForeignKey(
        'main.Cell', verbose_name="Ячейка", null=True, blank=True
    )
    additional_data = JSONField(
        verbose_name="Дополнительные параметры", null=True, blank=True
    )

    class Meta:
        app_label = 'main'
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"
