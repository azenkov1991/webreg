import datetime
from django.db import models
from catalogs.models import OKMUService
from .specialist import Specialist

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
        'main.ProfileSettings', verbose_name="Настройки профиля"
    )
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
            number_of_used__gte=models.F('number')
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

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профиля пользователей"
