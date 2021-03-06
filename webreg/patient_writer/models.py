import datetime
from django.db import models


class SlotTypeConfig(models.Model):
    slot_type = models.OneToOneField(
        'main.SlotType', verbose_name="Тип слота"
    )
    min_age = models.PositiveIntegerField(
        default=0, verbose_name="Минимальный возраст"
    )
    max_age = models.PositiveIntegerField(
        default=200, verbose_name="Максимальный возраст"
    )

    class Meta:
        verbose_name = "Настройки типа слота"
        verbose_name_plural = "Настройки типов слотов"


class SpecializationConfig(models.Model):
    specialization = models.ForeignKey(
        "main.Specialization", verbose_name="Специализация"
    )
    department_config = models.ForeignKey(
        'patient_writer.DepartmentConfig'
    )
    slot_types = models.ManyToManyField(
        "main.SlotType", verbose_name="Разрешенные типы слотов"
    )
    service = models.ForeignKey(
        "main.Service",
        verbose_name="Назначаемая услуга",
    )
    enable = models.BooleanField(
        default=True, verbose_name="Вкл"
    )
    is_show_comment = models.BooleanField(
        default=False, verbose_name='Вывод комментария'
    )
    comment = models.CharField(
        max_length=512, verbose_name='Комментарий', blank=True, null=True
    )

    class Meta:
        unique_together = ('specialization', 'department_config')
        verbose_name = "Настройки для специализации"
        verbose_name_plural = "Настройки для специализаций"


class SpecialistConfig(models.Model):
    specialist = models.OneToOneField(
        "main.Specialist",
        verbose_name="Specialist"
    )
    service = models.ForeignKey(
        "main.Service",
        verbose_name="Услуга для назначения",
        null=True, blank=True,
        related_name="first_service_specialist"
    )
    service2 = models.ForeignKey(
        "main.Service",
        verbose_name="Услуга повторного приема",
        null=True, blank=True,
        related_name="second_service_specialist"
    )

    def __str__(self):
        return self.specialist.fio

    class Meta:
        verbose_name = "Настройки для специалиста"
        verbose_name_plural = "Настройки для специалистов"


class ClinicConfig(models.Model):
    clinic = models.OneToOneField(
        'main.Clinic', verbose_name="Мед. учреждение"
    )
    sms = models.BooleanField(
        default=True, verbose_name='SMS-уведомления'
    )
    phone = models.CharField(
        max_length=127, verbose_name='Телефон для отказов'
    )
    phone2 = models.CharField(
        max_length=127, verbose_name='Телефон для информирования'
    )
    logo = models.ImageField(
        verbose_name='Логотип', blank=True, null=True, upload_to='logos'
    )
    send_sms = models.BooleanField(
        verbose_name="Посылать СМС ?", default=True
    )
    find_only_attached = models.BooleanField(
        verbose_name="Искать только прикрепленных пациентов",
        default=True
    )

    def __str__(self):
        return self.clinic.name

    class Meta:
        verbose_name = "Настройки мед. учреждения"
        verbose_name_plural = "Настройки мед. учреждений"


class DepartmentConfig(models.Model):
    department = models.OneToOneField(
        'main.Department', verbose_name="Подразделение"
    )
    specializations = models.ManyToManyField(
        'main.Specialization', through=SpecializationConfig
    )
    day_start_offset = models.PositiveIntegerField(
        default=1, verbose_name='Отступ начала записи'
    )
    today_time_interval = models.PositiveIntegerField(
        default=60, verbose_name='Защитный интервал записи в текущий день',
        help_text='Минуты'
    )
    day_range = models.PositiveIntegerField(
        default=0, verbose_name='Период записи'
    )
    phone = models.CharField(
        max_length=31, verbose_name='Телефон для отказов', blank=True, null=True
    )
    phone2 = models.CharField(
        max_length=31, verbose_name='Телефон для информирования', blank=True, null=True
    )
    min_age = models.PositiveIntegerField(
        default=0, verbose_name='Минимальный возраст'
    )
    max_age = models.PositiveIntegerField(
        default=200, verbose_name='Максимальный возраст'
    )
    order = models.PositiveIntegerField(
        verbose_name="Порядок", default=0,
    )

    def __str__(self):
        return '{0}, {1}'.format(self.department.name, self.department.address)

    def save(self, *args, **kwargs):
        if self.day_start_offset > self.day_range:
            self.day_start_offset = self.day_range
        super(DepartmentConfig, self).save(*args, **kwargs)

    def get_date_range(self):
        start_date = datetime.date.today() + datetime.timedelta(self.day_start_offset)
        end_date = datetime.date.today() + datetime.timedelta(self.day_range)
        return start_date, end_date

    class Meta:
        verbose_name = 'Настройки подразделения'
        verbose_name_plural = 'Настройки подразделений'



