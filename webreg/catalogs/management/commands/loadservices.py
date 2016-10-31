# -*- coding: utf-8 -*-
from qmsmodule.qmsfunctions import *
from catalogs.models import OKMUService
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.conf import settings


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-c', '--clinic', action='store', dest='clinic', type='int', default=False, help='id clinic'),
    )

    def handle(self, *args, **options):
        if 'clinic' not in options:
            raise CommandError('Clinic parameter required')
        id_clinic = options['clinic']
        clinic = Clinic.objects.filter(id=id_clinic)
        if clinic:
            cache_settings = clinic[0].qms_connection.connection_params
            self.load_okmu(cache_settings)
            print('complete!')
        else:
            raise CommandError('Clinic not found')

    def load_okmu(self, cache_settings):
        """
        Загрузка справочников ОКМУ из qms
        """
        qms = QMS(cache_settings, 'loadservices'))
        query = qms.query

        for level in range(1, 5):
            query.execute_query('LoadOKMU', cache_settings['DATABASE_CODE'], level)
            for service_fields_list in query.results():
                code = service_fields_list[0]
                name = service_fields_list[1]
                parent = service_fields_list[2]
                if code is not None and name is not None:
                    service = OKMUService(code=code, name=name)
                    if parent is not None:
                        try:
                            parent_service = OKMUService.objects.get(pk=parent)
                        except OKMUService.DoesNotExist:
                            print(parent)
                        else:
                            service.parent = parent_service
                    service.save()


def load_mkb(self, cache_settings):
    query = QMS(cache_settings, set_logger_settings(join(settings.STATIC_LOG_ROOT, 'log'), 'loadservices')).query
    for level in range(1, 5):
        query.execute_query('LoadMKB', cache_settings['DATABASE_CODE'], level)
        for service_fields_list in query.results():
            code = service_fields_list[0]
            name = service_fields_list[1]
            is_finished = (level >= 4)
            if code is not None and name is not None:
                service = OKMUService(code=code, name=name)
                service.save()
