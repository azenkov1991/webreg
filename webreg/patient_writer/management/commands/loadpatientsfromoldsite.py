from logging import getLogger
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from main.models import UserProfile, Patient
from main.logic import find_patient_by_polis_number
from qmsintegration.models import QmsDB, set_external_id, get_external_id, IdMatchingTable
from qmsmodule.qmsfunctions import QMS

logger = getLogger("command_manage")


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
    def handle(self, *args, **options):
        try:
            qmsdb1 = QmsDB.objects.get(id=1)
            qmsdb2 = QmsDB.objects.get(id=2)
        except QmsDB.DoesNotExist:
            raise CommandError("Нет описания баз данных Qms")
        qms1 = QMS(qmsdb1.settings)
        qms2 = QMS(qmsdb2.settings)
        profile = UserProfile.objects.get(name=settings.PATIENT_WRITER_PROFILE)
        for ext_user in OldUser.objects.using("old_db").all():
            if ext_user.qqc153 and not IdMatchingTable.objects.filter(external_id=ext_user.qqc153).exists():
                logger.info('trying to find ' + ext_user.username)
                if ext_user.qqc153[:3] == "vAB":
                    qms = qms1
                    qmsdb=qmsdb1
                elif ext_user.qqc153[:3] == "vAC":
                    qms = qms2
                    qmsdb = qmsdb2
                else:
                    logger.error('qqc неизвестной базы ' + ext_user.qqc153)
                    continue

                patient_information = qms.get_patient_information(patient_qqc=ext_user.qqc153)
                if patient_information and patient_information['polis_number']:
                    patient = find_patient_by_polis_number(patient_information['polis_number'], patient_information['birth_date'])
                    if patient:
                        if patient.clinic.id != qmsdb.clinic.id:
                            logger.error('Пациент прикреплен к двум базам ' + str(patient))
                            continue
                        if ext_user.qqc153 != get_external_id(patient, qmsdb):
                            logger.error('qqc пациента не совпадает' + str(patient))
                            continue
                        logger.info("saving " + ext_user.username)
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
                        patient.phone = ext_user.phone
                        patient.user = user
                        patient.save()






