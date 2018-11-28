from django.db import models


class ProfileSettings(models.Model):
    name = models.CharField(
        max_length=128, verbose_name="Наименование настроек"
    )
    slot_restrictions = models.ManyToManyField(
        'main.SlotType', through='main.SlotRestriction',
        verbose_name="Ограничения на тип ячейки"
    )
    service_restrictions = models.ManyToManyField(
        'main.Service', through='main.ServiceRestriction',
        verbose_name="Доступные для назначения услуги"
    )
    specialist_restrictions = models.ManyToManyField(
        'main.Specialist', through='main.SpecialistRestriction',
         verbose_name="Доступные для назначения специалисты"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Настройки профиля"
        verbose_name_plural = "Настройки профилей"


class SlotRestriction(models.Model):
    profile_settings = models.ForeignKey(
        ProfileSettings, verbose_name="Настройки профиля пользователя"
    )
    slot_type = models.ForeignKey(
        'main.SlotType', verbose_name="Тип ячейки"
    )

    class Meta:
        verbose_name = "Разрешение на тип ячейки"
        verbose_name_plural = "Разрешения на тип ячейки"


class ServiceRestriction(models.Model):
    profile_settings = models.ForeignKey(
        ProfileSettings, verbose_name="Настройки профиля пользователя"
    )
    service = models.ForeignKey(
        'main.Service', verbose_name="Услуга"
    )

    class Meta:
        unique_together = ('profile_settings', 'service')
        verbose_name = "Разрешение назначить услугу"
        verbose_name_plural = "Разрешения на назначения услуг"


class SpecialistRestriction(models.Model):
    profile_settings = models.ForeignKey(
        'main.ProfileSettings', verbose_name="Настройки профиля пользователя"
    )
    specialist = models.ForeignKey(
        'main.Specialist', verbose_name="Специалист"
    )

    class Meta:
        app_label = 'main'
        unique_together = ('profile_settings', 'specialist')
        verbose_name = "Разрешенный для назначения специалист"
        verbose_name_plural = "Разрешенные для назначений специалисты"
