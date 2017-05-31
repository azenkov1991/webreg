from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from main.models import UserProfile, Patient
from qmsintegration.models import QmsDB, set_external_id
from qmsmodule.qmsfunctions import QMS


class OldUser(models.Model):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        max_length=128,
        unique=True,
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'))
    qqc153 = models.CharField(
        max_length=63, verbose_name='qqc153',
        blank=True, null=True,
        db_column="qqc153"
    )
    cityId = models.IntegerField(
        verbose_name='Город', blank=True, null=True,
        db_column='city_id'
    )
    phone = models.CharField(
        max_length=31, verbose_name='Телефон',
        blank=True, null=True,
        db_column='phone'
    )

    class Meta:
        managed = False
        db_table = "auth_user"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")

    def handle(self, *args, **options):
        dbname=options['dbname']
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except QmsDB.DoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        qms = QMS(qmsdb.settings)
        profile = UserProfile.objects.get(name=settings.PATIENT_WRITER_PROFILE)
        for ext_user in OldUser.objects.using("old_db").all():
            if ext_user.qqc153:
                patient_information = qms.get_patient_information(patient_qqc=ext_user.qqc153)
                if patient_information:
                    print("load " + ext_user.username)
                    user = User.objects.create(
                        username=ext_user.username,
                        password=ext_user.password,
                        first_name=ext_user.first_name,
                        last_name=ext_user.last_name,
                        email=ext_user.email,
                        is_staff=ext_user.is_staff,
                        is_active=ext_user.is_active,
                        date_joined=ext_user.date_joined,
                    )
                    profile.user.add(user)
                    patient = Patient.objects.create(
                        first_name=patient_information['first_name'],
                        last_name=patient_information['last_name'],
                        middle_name=patient_information['middle_name'],
                        birth_date=patient_information['birth_date'],
                        polis_number=patient_information['polis_number'],
                        polis_seria= patient_information['polis_seria'],
                        phone=ext_user.phone,
                        user_id=user.id,
                        clinic_id=qmsdb.clinic.id
                    )
                    set_external_id(patient, ext_user.qqc153)





