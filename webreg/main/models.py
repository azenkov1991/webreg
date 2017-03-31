import logging
import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator
from django.db.models import F
from mixins.models import TimeStampedModel, SafeDeleteMixin
from django.contrib.sites.models import Site
from catalogs.models import OKMUService
from main.validators import oms_polis_number_validation, birth_date_validation

log = logging.getLogger("webreg")


class AppointmentError(Exception):
    pass

class PatientError(Exception):
    pass

class UserProfile(models.Model):
    user = models.ManyToManyField('auth.User')
    clinic = models.ForeignKey('Clinic', verbose_name="Мед. учреждение", null=True, blank=True)
    profile_settings = models.ForeignKey('main.ProfileSettings', verbose_name="Настройки профиля")
    site = models.ForeignKey('sites.Site', verbose_name="Сайт")

    def get_slot_restrictions(self):
        """
        :return:
        Возвращает query_set типов слотов
        """
        return self.profile_settings.slot_restrictions.all()

    def get_allowed_specialists(self, initial_specialist_query_set=None):
        """

        :param initial_specialist_query_set:
        Если передан specialist_query_set услуг, то выборка из него происходит
        :return:
        Возвращает доступных для назначения специалистов
        """
        if not initial_specialist_query_set:
            initial_specialist_query_set=Specialist.objects.all()

        # проверка на ограничение разрешенных для назначений специалистов

        specialist_restrictions = self.profile_settings.specialist_restrictions.all()
        if not specialist_restrictions.exists():
            specialist_restrictions = initial_specialist_query_set

        return initial_specialist_query_set & specialist_restrictions


    def get_allowed_services(self, initial_service_query_set=None):
        """
        :param initial_service_query_set:
         Если передан QuerySet услуг, то выборка из него происходит
        :return:
        Возвращает доступные для назначения услуги
        """

        if not initial_service_query_set:
            initial_service_query_set = OKMUService.objects.all()

        # проверка на ограничение услуг сайта
        try:
            site_allowed_services = self.site.siteservicerestriction.services.all()
            if not site_allowed_services.exists():
                site_allowed_services = initial_service_query_set
        except models.RelatedObjectDoesNotExist:
            site_allowed_services = initial_service_query_set

        # проверка на ограничение разрешенных для назначений услуг
        profile_allowed_services = self.profile_settings.service_restrictions.all()
        if not profile_allowed_services.exists():
            profile_allowed_services = initial_service_query_set

        # проверка на ограничение количества услуг
        now_date = datetime.datetime.now()

        service_id_list = self.numberofservicerestriction_set.filter(
            date_start__lte=now_date, date_end__gte=now_date,
            number_of_used__gte=F('number')
        ).values_list("service_id",flat=True)

        return (initial_service_query_set & site_allowed_services & profile_allowed_services).exclude(
            id__in=service_id_list
        )

    def users_str(self):
        """
        Возвращает строку пользователя или первых 5-ти пользователей
        Используется для отображения в админке
        """
        if self.user.count() > 5:
            return " ".join(map(lambda user: str(user),  self.user.all()[:5])) + "..."
        else:
            return " ".join(map(lambda user: str(user),  self.user.all()))

    users_str.short_description="Пользователи"


    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профиля пользователей"


class ProfileSettings(models.Model):
    name = models.CharField(max_length=128, verbose_name="Наименование настроек")
    slot_restrictions = models.ManyToManyField('main.SlotType', through='main.SlotRestriction',
                                               verbose_name="Ограничения на тип ячейки")
    service_restrictions = models.ManyToManyField('catalogs.OKMUService', through='main.ServiceRestriction',
                                                  verbose_name="Доступные для назначения услуги")
    specialist_restrictions = models.ManyToManyField('main.Specialist', through='main.SpecialistRestriction',
                                                   verbose_name="Доступные для назначения специалисты")

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
    number = models.PositiveIntegerField(verbose_name="Номер кабинета", null=True)
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
    birth_date = models.DateField(verbose_name="Дата рождения",
                                  validators=[birth_date_validation,])
    polis_number = models.CharField(max_length=16,
                                    verbose_name="Номер полиса",
                                    null=True)
    polis_seria = models.CharField(max_length=6, verbose_name="Серия полиса",
                                   null=True, blank=True)

    clinic = models.ManyToManyField('main.Clinic', verbose_name="Мед. учреждение")

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


class ServiceRestriction(models.Model):
    profile_settings = models.ForeignKey(ProfileSettings, verbose_name="Настройки профиля пользователя")
    service = models.ForeignKey('catalogs.OKMUService', verbose_name="Услуга")

    class Meta:
        verbose_name = "Разрешение назначить услугу"
        verbose_name_plural = "Разрешения на назначения услуг"


class SpecialistRestriction(models.Model):
    profile_settings = models.ForeignKey('main.ProfileSettings', verbose_name="Настройки профиля пользователя")
    specialist = models.ForeignKey('main.Specialist', verbose_name="Специалист")

    class Meta:
        verbose_name = "Разрешенный для назначения специалист"
        verbose_name_plural = "Разрешенные для назначений специалисты"


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


class SiteServiceRestriction(models.Model):
    services = models.ManyToManyField("catalogs.OKMUService", verbose_name="Услуга")
    site = models.OneToOneField("sites.Site", verbose_name="Сайт")


    class Meta:
        verbose_name = "Разрашеение на назначение услуг на сайте"
        verbose_name_plural = "Разрешения на назначения услуг на сайтах"










