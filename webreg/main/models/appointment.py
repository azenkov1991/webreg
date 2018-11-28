from django.db import models
from django.contrib.postgres.fields import JSONField
from main.tasks import send_sms
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
        "main.Service", verbose_name="Услуга"
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

    def send_sms(self):
        valid_phone = self.patient.phone.startswith('89') or \
                      self.patient.phone.startswith('79') or self.patient.phone.startswith('+79')
        if self.patient.phone and self.specialist.department.clinic.clinicconfig.send_sms and valid_phone:
            spec_mem = self.specialist.fio.split(' ')
            if len(spec_mem):
                spec_mem = spec_mem[0]
            else:
                spec_mem = self.specialist.fio
            message = 'Вы записаны в {dep} на {date}, {time}. Врач:{spec}'.format(
                dep=self.specialist.department.name, addr=self.specialist.department.address,
                date=self.date.strftime('%d.%m.%y'), time=self.cell.time_start,
                spec=spec_mem
            )
            if self.cell.cabinet:
                message += ' Каб.{0}'.format(self.cell.cabinet.number)
            send_sms.delay({'message': message[:400], 'target': self.patient.phone})

    class Meta:
        app_label = 'main'
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"
