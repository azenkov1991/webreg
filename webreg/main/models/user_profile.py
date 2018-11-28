import datetime
from django.db import models
from .service import Service
from django.conf import settings, ImproperlyConfigured
from .specialist import Specialist
from .profile_settings import ProfileSettings
from .slot_type import SlotType


def get_default_profile_settings():
    try:
        name = settings.DEFAULT_PROFILE_SETTINGS_NAME
        default_profile_settinngs = ProfileSettings.objects.get(name=name).id
    except ProfileSettings.DoesNotExist:
        raise ImproperlyConfigured("Не выбраны настройки профиля по умолчанию")
    return default_profile_settinngs


class UserProfile(models.Model):
    name = models.CharField(
        max_length=256, verbose_name="Имя профиля"
    )
    user = models.ManyToManyField('auth.User')
    clinic = models.ForeignKey(
        'Clinic', verbose_name="Мед. учреждение",
        null=True, blank=True
    )
    profile_settings = models.ForeignKey(
        'main.ProfileSettings', verbose_name="Настройки профиля",
        on_delete=models.SET(get_default_profile_settings),
        default=get_default_profile_settings
    )
    site = models.ForeignKey('sites.Site', verbose_name="Сайт")

    def get_slot_restrictions(self):
        """
        :return:
        Возвращает query_set типов слотов
        """
        return self.profile_settings.slot_restrictions.all()

    def get_allowed_slots(self, initial_slot_query_set=None):
        """
        :return:
        Возвращает query_set разрешенных типов слотов
        """
        if initial_slot_query_set is None:
            slot_restrictions = self.profile_settings.slot_restrictions.all()
        if slot_restrictions.exists():
            return slot_restrictions
        else:
            return SlotType.objects.all()

    def get_allowed_specialists(self, initial_specialist_query_set=None):
        """
        :param initial_specialist_query_set:
        Если передан specialist_query_set услуг, то выборка из него происходит
        :return:
        Возвращает доступных для назначения специалистов
        """
        if initial_specialist_query_set is None:
            initial_specialist_query_set = Specialist.objects.all()

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

        if initial_service_query_set is None:
            initial_service_query_set = Service.objects.all()

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
            number_of_used__gte=models.F('number')
        ).values_list("service_id", flat=True)

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

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профиля пользователей"
