import logging
import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from mixins.models import TimeStampedModel, SafeDeleteMixin
from django.contrib.sites.models import Site
from catalogs.models import OKMUService

log = logging.getLogger("webreg")


class AppointmentError(Exception):
    pass


class UserProfile(models.Model):
    user = models.ForeignKey('auth.User')
    clinic = models.ForeignKey('Clinic', verbose_name="Мед. учреждение", null=True, blank=True)
    profile_settings = models.ForeignKey('main.ProfileSettings', verbose_name="Настройки профиля")
    site = models.ForeignKey('sites.Site', verbose_name="Сайт")

    def get_slot_restrictions(self):
        """
        :return:
        Возвращает query_set типов слотов
        """
        return self.profile_settings.slot_restrictions.all()

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профиля пользователей"


class ProfileSettings(models.Model):
    name = models.CharField(max_length=128, verbose_name="Наименование настроек")
    slot_restrictions = models.ManyToManyField('main.SlotType', through='main.SlotRestriction',
                                               verbose_name="Ограничения на тип ячейки")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Настройки профиля"
        verbose_name_plural = "Настройки профилей"


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


class Specialist(SafeDeleteMixin):
    fio = models.CharField(max_length=128, verbose_name="Полное имя")
    specialization = models.ForeignKey(Specialization, verbose_name="Специализация")
    performing_services = models.ManyToManyField("catalogs.OKMUService", verbose_name="Выполняемые услуги")
    department = models.ForeignKey(Department, verbose_name="Подразделение")

    def __str__(self):
        return self.fio

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"


class Cabinet(models.Model):
    number = models.PositiveIntegerField(verbose_name="Номер кабинета")
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
        max_length=128, verbose_name="Имя", unique=True,
    )
    color = models.CharField(
        max_length=7, verbose_name="Цвет", help_text="HEX color, as #RRGGBB", blank=True, null=True
    )
    clinic = models.ForeignKey(
        Clinic, verbose_name="Мед. учреждение"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип слота"
        verbose_name_plural = "Типы слотов"


class Cell(models.Model):
    date = models.DateField(verbose_name="Дата приема", db_index=True)
    time_start = models.TimeField(verbose_name="Время приема")
    time_end = models.TimeField(verbose_name="Окончание приема")
    specialist = models.ForeignKey(Specialist, verbose_name="Специалист")
    cabinet = models.ForeignKey(Cabinet, verbose_name="Кабинет", null=True, blank=True)
    performing_services = models.ManyToManyField("catalogs.OKMUService", verbose_name="Выполняемые услуги", blank=True)
    slot_type = models.ForeignKey(SlotType, verbose_name="Тип слота", null=True, blank=True)
    free  = models.BooleanField(verbose_name="Свободна", default=True)
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
        cells_in_cabinet = today_cells.filter(cabinet=cell.cabinet) if cell.cabinet else []
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
            raise ValidationError({NON_FIELD_ERRORS: ["Время окончания приема должно быть больше времени начала"]})

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
        permissions = (
            ("view_timetable", "Разрешение на просмотр расписания"),
        )


class Appointment(TimeStampedModel, SafeDeleteMixin):
    user_profile = models.ForeignKey(UserProfile, verbose_name="Профиль пользователя")
    date = models.DateField(verbose_name="Дата приема", db_index=True)
    specialist = models.ForeignKey(Specialist, verbose_name="Специалист")
    service = models.ForeignKey("catalogs.OKMUService", verbose_name="Услуга")
    patient = models.ForeignKey(Patient, verbose_name="Пациент")
    cell = models.ForeignKey(Cell, verbose_name="Ячейка", null=True, blank=True)
    additional_data = JSONField(verbose_name="Дополнительные параметры", null=True, blank=True)

    class Meta:
        verbose_name = "Назначение"
        verbose_name_plural = "Назначения"


class SlotRestriction(models.Model):
    profile_settings = models.ForeignKey(ProfileSettings, verbose_name="Настройки профиля пользователя")
    slot_type = models.ForeignKey(SlotType, verbose_name="Тип ячейки")

    class Meta:
        verbose_name = "Разрешение на тип ячейки"
        verbose_name_plural = "Разрешения на тип ячейки"


class NumberOfServiceRestriction(models.Model):
    service = models.ForeignKey("catalogs.OKMUService", verbose_name="Услуга")
    number = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Количество")
    number_of_used = models.IntegerField(validators=[MinValueValidator(0)],
                                         verbose_name="Количество назначенныхх",
                                         default=0,
                                         )
    user_profile = models.ForeignKey(UserProfile, verbose_name="Профиль пользователя")
    date_start = models.DateField(verbose_name="Начало действия ограничения")
    date_end = models.DateField(verbose_name="Конец действия ограничения")

    @property
    def remain(self):
        return self.number - self.number_of_used

    def increment(self):
        self.number_of_used += 1
        self.save()

    @classmethod
    def get_restriction(cls, date, user_profile, service):
        restriction = None
        try:
            restriction = NumberOfServiceRestriction.objects.get(date_start__lte=date, date_end__gte=date,
                                                                 user_profile=user_profile,
                                                                 service=service)
        except NumberOfServiceRestriction.DoesNotExist:
            pass
        return restriction

    def full_clean(self, exclude=None, validate_unique=True):
        try:
            super(NumberOfServiceRestriction, self).full_clean(None, validate_unique)
        except ValidationError as e:
            raise e
        else:
            if NumberOfServiceRestriction.objects.filter(
                service=self.service,
                user_profile=self.user_profile,
                date_start__range=[self.date_start, self.date_end]
            ).exists():
                raise ValidationError("Ограничение на заданный период уже существует")

            if NumberOfServiceRestriction.objects.filter(
                service=self.service,
                user_profile=self.user_profile,
                date_end__range=[self.date_start, self.date_end]
            ).exists():
                raise ValidationError("Ограничение на заданный период уже существует")

    class Meta:
        verbose_name = "Ограничение на кол-во услуг"
        verbose_name_plural = "Ограничения на кол-во услуг"


class SiteServicePermission(models.Model):
    services = models.ManyToManyField("catalogs.OKMUService", verbose_name="Услуга")
    site = models.OneToOneField("sites.Site", verbose_name="Сайт")

    class Meta:
        verbose_name = "Разрашеение на назначение услуг"
        verbose_name_plural = "Разрешения на назначения услуг"










