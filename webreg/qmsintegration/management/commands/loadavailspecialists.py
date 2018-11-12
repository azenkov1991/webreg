from django.core.management.base import BaseCommand, CommandError
from logging import getLogger
from main.models import UserProfile, SpecialistRestriction
from qmsintegration.models import QmsDB, QmsIntegrationError, get_internal_id, QmsUser
from qmsmodule.qmsfunctions import QMS


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("user_profile_name", help="Имя профиля пользователя")

    def handle(self, *args, **options):
        dbname = options['dbname']
        user_profile_name = options['user_profile_name']
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except QmsDB.DoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)

        try:
            user_profile = UserProfile.objects.get(name=user_profile_name)
        except UserProfile.DoesNotExist:
            raise CommandError("Нет профиля пользователя с именем " + user_profile_name)

        try:
            qms_user = QmsUser.objects.get(
                user_profile=user_profile, qmsdb=qmsdb
            )
        except QmsUser.DoesNotExist:
            raise CommandError("Для профиля " + user_profile.name + " не найден пользователь qms")

        logger = getLogger("command_manage")
        qms = QMS(qmsdb.settings)
        qqc244list = qms.get_avail_spec_qqc_list(qms_user.qqc244)
        old_restriction_set_ids = set(SpecialistRestriction.objects.filter(
            profile_settings_id=user_profile.profile_settings.id,
        ).values_list('id', flat=True))
        new_restriction_set_ids = set()
        for qqc244 in qqc244list:
            try:
                specialist_id = get_internal_id("244", qqc244)
                restriction, created = SpecialistRestriction.objects.get_or_create(
                    specialist_id=specialist_id,
                    profile_settings_id=user_profile.profile_settings.id
                )
                new_restriction_set_ids.add(restriction.id)
            except QmsIntegrationError:
                logger.error("Не найден специалист " + qqc244)

        # Удаление старых разрешений
        to_removal_set_ids = old_restriction_set_ids - new_restriction_set_ids
        for restriction_id in to_removal_set_ids:
            try:
                SpecialistRestriction.objects.get(id=restriction_id).delete()
            except SpecialistRestriction.DoesNotExist:
                pass


