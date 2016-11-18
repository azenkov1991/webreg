import logging
import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.postgres.fields import JSONField
from catalogs.models import OKMUService
from qmsintegration import decorators as qms
from mixins.models import TimeStampedModel

log = logging.getLogger("webreg")


class AppointmentError(Exception):
    pass


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
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"


class Specialization(models.Model):
    name = models.CharField(max_length=128, verbose_name='Специализация', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"


class Specialist(models.Model):
    fio = models.CharField(max_length=128, verbose_name="Полное имя")
    specialization = models.ForeignKey(Specialization, verbose_name="Специализация")
    performing_services = models.ManyToManyField(OKMUService, verbose_name="Выполняемые услуги")
    department = models.ForeignKey(Department, verbose_name="Подразделение")
    IsActive = models.BooleanField(verbose_name="Активен")

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


class Patient(models.Model):
    first_name = models.CharField(max_length=128, verbose_name="Фамилия")
    last_name = models.CharField(max_length=128, verbose_name="Имя")
    middle_name = models.CharField(max_length=128, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    polis_number = models.CharField(max_length=16, verbose_name="Номер полиса")

    @property
    def fio(self):
        return self.first_name + " " + self.last_name + " " + self.middle_name

    def __str__(self):
        return self.first_name + " " + self.last_name[0] + ". " + \
               self.middle_name[0] + "., " + self.birth_date.strftime("%d.%m.%Y")

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"


class SlotType(models.Model):
    name = models.CharField(
        max_length=128, verbose_name="Имя"
    )
    color = models.CharField(
        max_length=7, verbose_name="Цвет", help_text="HEX color, as #RRGGBB", blank=True, null=True
    )
    clinic = models.ForeignKey(
        Clinic, verbose_name="Мед. учреждение"
    )


class Cell(models.Model):
    date = models.DateField(verbose_name="Дата приема", db_index=True)
    time_start = models.TimeField(verbose_name="Время приема")
    time_end = models.TimeField(verbose_name="Окончание приема")
    specialist = models.ForeignKey(Specialist, verbose_name="Специалист")
    cabinet = models.ForeignKey(Cabinet, verbose_name="Кабинет", null=True, blank=True)
    performing_services = models.ManyToManyField(OKMUService, verbose_name="Выполняемые услуги")
    slot_type = models.ForeignKey(SlotType, verbose_name="Тип слота", null=True, blank=True)

    @property
    def time_str(self):
        return '%s-%s' % (self.time_start.strftime('%H:%M'), self.time_end.strftime('%H:%M'))

    def __str__(self):
        return self.date.strftime("%d.%m.%Y") + " " + self.time_start.strftime("%H:%M") + "-" +\
               self.time_end.strftime("%H:%M") + " " + str(self.cabinet) + " " + str(self.specialist)

    def full_clean(self, exclude=None, validate_unique=True):
        try:
            super(Cell, self).full_clean(None, validate_unique)
        except ValidationError as e:
            raise e
        else:
            Cell.save_cell_validation(self)

    @classmethod
    def save_cell_validation(cls, cell):
        today_cells = Cell.objects.filter(date=cell.date).exclude(id=cell.id)
        cells_in_cabinet = today_cells.filter(cabinet=cell.cabinet)
        # проверка пересечения ячеек в кабинете
        for other_cell in cells_in_cabinet:
            if cell.intersection(other_cell):
                raise ValidationError({NON_FIELD_ERRORS: ["Ячека пересекается с другой ячейкой по кабинету"]})
        # проверка пересечения ячеек у специалиста
        specialists_cells = today_cells.filter(specialist=cell.specialist)
        for other_cell in specialists_cells:
            if cell.intersection(other_cell):
                raise ValidationError("Ячека пересекается с другой ячейкой у специалиста")
        if cell.time_end <= cell.time_start:
            raise ValidationError({NON_FIELD_ERRORS: ["Время оканчания приема должно быть больше времени начала"]})

    def intersection(self, cell):
        if (((cell.time_start <= self.time_start) and (self.time_start < cell.time_end)) or
                ((cell.time_start < self.time_end) and (self.time_end <= cell.time_end))):
            return True
        if (((self.time_start <= cell.time_start) and (cell.time_start < self.time_end)) or
                ((self.time_start < cell.time_end) and (cell.time_end <= self.time_end))):
            return True
        return False

    class Meta:
        verbose_name = "Ячейка"
        verbose_name_plural = "Ячейки"


class Appointment(TimeStampedModel):
    date = models.DateField(verbose_name="Дата приема", db_index=True)
    specialist = models.ForeignKey(Specialist, verbose_name="Специалист")
    service = models.ForeignKey(OKMUService, verbose_name="Услуга")
    patient = models.ForeignKey(Patient, verbose_name="Пациент")
    cell = models.ForeignKey(Cell, verbose_name="Ячейка", null=True, blank=True)
    additional_data = JSONField(verbose_name="Дополнительные параметры", null=True, blank=True)

    @qms.create_appointment
    @classmethod
    def create_appointment(cls, patient, specialist, service, date, cell=None, additional_data=None):
        exception_details = "Пациент: " + patient.fio + " Специалист: " + specialist.fio + \
                            " Дата: " + str(date)
        if cell:
            exception_details += " Время: " + str(cell.time_start)
        # вызвать исключение если ячейка занята
        if cell and cell.appointment_set.exists():
            raise AppointmentError("Попытка назначения в занятую ячейку." + exception_details)
        # если назначение на дату и время меньше текущего
        if date < datetime.date.today():
            raise AppointmentError("Попытка назначения в прошлое." + exception_details)
        # если специалист не выполняет услугу
        if not specialist.performing_services.filter(code=service.code).exists():
            raise AppointmentError("Попытка назначение услуги, которую специалист не выполняет." + exception_details)
        # eсли ячейка не принадлежит специалисту
        if cell and (cell.specialist != specialist):
            raise AppointmentError("Ячейка не принадлежит специалисту." + exception_details)
        try:
            appointment = Appointment(date=date, specialist=specialist, service=service,
                                      patient=patient)
            if cell:
                appointment.cell = cell
            if additional_data:
                appointment.additional_data = additional_data
            appointment.save()
            return appointment
        except Exception as ex:
            log.error(str(ex))
            raise AppointmentError("Ошибка при сохранении модели назначения" + exception_details)

    class Meta:
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"







