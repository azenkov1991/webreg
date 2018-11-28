from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class NumberOfServiceRestriction(models.Model):
    service = models.ForeignKey(
        "main.Service", verbose_name="Услуга"
    )
    number = models.IntegerField(
        validators=[MinValueValidator(0)], verbose_name="Количество"
    )
    number_of_used = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Количество назначенныхх",
        default=0,
    )
    user_profile = models.ForeignKey(
        'main.UserProfile', verbose_name="Профиль пользователя"
    )
    date_start = models.DateField(
        verbose_name="Начало действия ограничения"
    )
    date_end = models.DateField(
        verbose_name="Конец действия ограничения"
    )

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
            restriction = NumberOfServiceRestriction.objects.get(
                date_start__lte=date, date_end__gte=date,
                user_profile=user_profile,
                service=service
            )
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
        app_label = 'main'
        verbose_name = "Ограничение на кол-во услуг"
        verbose_name_plural = "Ограничения на кол-во услуг"
