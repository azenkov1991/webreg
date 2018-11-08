from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import  BaseCommand, CommandError
from main.models import SiteConfig, UserProfile, ProfileSettings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('domain', type=str, help="Имя сайта для создания объекта сайт")

    def handle(self, *args, **options):
        domain = options['domain']
        site, created = Site.objects.get_or_create(
            domain=domain,
            defaults={
                'name': 'Patient writer'
            }
        )
        print('Сайт создан')

        site_config, created = SiteConfig.objects.get_or_create(
            site_id=site.id,
            login_url='/pwriter/input_first_step/'
        )

        print('Конфигурация сайта по умолчанию создана')
        patient_writer_username = settings.PATIENT_WRITER_USER
        user, created = User.objects.get_or_create(
            username=patient_writer_username,
            defaults={
                'is_active': True
            }
        )
        print('Создан пользователь ' + patient_writer_username)

        patient_writer_profile_name = settings.PATIENT_WRITER_PROFILE

        user_profile_settings_name = settings.PATIENT_WRITER_PROFILE + '_settings'

        profile_settings, created = ProfileSettings.objects.get_or_create(
            name=user_profile_settings_name
        )

        user_profile, created = UserProfile.objects.get_or_create(
            name=patient_writer_profile_name,
            defaults={
                'site': site,
                'profile_settings': profile_settings
            }
        )
        user_profile.user.add(user)
        print("Создан профиль пользователя по умолчанию")








