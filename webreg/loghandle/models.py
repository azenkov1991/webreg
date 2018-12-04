from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from main.models import Patient
from main.middleware import GlobalRequestMiddleware


class LogModel(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    time = models.TimeField(auto_now_add=True, verbose_name="Время")
    level = models.CharField(max_length=256, verbose_name="Уровень", db_index=True)
    logger_name = models.CharField(max_length=256, verbose_name="Логгер")
    source_file = models.CharField(max_length=1024, verbose_name="Источник")
    message = models.TextField(verbose_name="Сообщение")
    session_key = models.CharField(
        max_length=127, verbose_name="Ключ сессии", blank=True, null=True
    )

    class Meta:
        verbose_name = "Лог"
        verbose_name_plural = "Логи"


class UserAction(models.Model):
    date = models.DateField(
        auto_now_add=True, verbose_name="Дата"
    )
    time = models.TimeField(
        auto_now_add=True, verbose_name="Время"
    )
    session_key = models.CharField(
        max_length=127, verbose_name="Ключ сессии", blank=True, null=True
    )
    user_id = models.IntegerField(
        verbose_name="Пользователь", null=True, blank=True,
    )
    patient_id = models.IntegerField(
        verbose_name="ID Пациента", null=True, blank=True,
    )
    action = models.CharField(
        max_length=255, verbose_name="Действие"
    )
    info = JSONField(
        verbose_name="Информация о действии", null=True, blank=True
    )

    def patient(self):
        try:
            return str(Patient.objects.get(pk=self.patient_id))
        except Patient.DoesNotExist:
            return None

    def user(self):
        try:
            return str(User.objects.get(pk=self.user_id))
        except User.DoesNotExist:
            return None
    user.short_description = "Пользователь"
    patient.short_description = "Пациент"

    @classmethod
    def log(cls, action, info=None, user_id=None):
        request = GlobalRequestMiddleware.get_current_request()
        if request:
            if not user_id:
                user_id = request.user.id
            patient_id = request.session.get('patient_id', None)
        else:
            patient_id = None
        log = cls(
            user_id=user_id, patient_id=patient_id, action=action, info=info,
            session_key=request.session.session_key,
        )
        log.save()

    class Meta:
        verbose_name = "Дейсвие пользователя"
        verbose_name_plural = "Дейсвия пользователей"



