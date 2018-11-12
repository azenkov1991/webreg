from django.core.management.base import BaseCommand, CommandError
from main.models import UserProfile, ServiceRestriction
from catalogs.models import OKMUService
from qmsintegration.models import QmsDB, QmsUser
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

        qms = QMS(qmsdb.settings)
        code_list = qms.get_avail_services_code_list(qms_user.qqc244)
        old_restriction_set_ids = set(ServiceRestriction.objects.filter(
            profile_settings_id=user_profile.profile_settings.id,
        ).values_list('id', flat=True))
        new_restriction_set_ids = set()
        for code in code_list:
            service, created = OKMUService.objects.get_or_create(code=code)
            restriction, created = ServiceRestriction.objects.get_or_create(
                service_id=service.id,
                profile_settings_id=user_profile.profile_settings.id
            )
            new_restriction_set_ids.add(restriction.id)

        # Удаление старых разрешений
        to_removal_set_ids = old_restriction_set_ids - new_restriction_set_ids
        for restriction_id in to_removal_set_ids:
            ServiceRestriction.objects.get(id=restriction_id).delete()


