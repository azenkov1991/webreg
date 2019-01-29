import  logging
from catalogs.models import *
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from main.models import Specialist, Department, Specialization, Service
from patient_writer.models import SpecialistConfig

logger = logging.getLogger("command_manage")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("--department", dest='department', help="Id подразделения", type=int)

    def cre_spec(self, fio, specialization, department_id, qqc244):
        spec = None
        try:
            spec = Specialist(fio=fio, specialization=specialization, department_id=department_id, deleted=False)
            spec.save()
            set_external_id(spec, qqc244)
        except Exception as ex:
            logger.error("Не удалось загрузить специалиста из qms " + qqc244 + ' ' + fio + "\n" +
                         str(ex))
        return spec

    def get_exist_specialist(self, qqc244):
        int_id = get_internal_id("244", qqc244)
        specialist = Specialist.all_objects.get(pk=int_id)
        return specialist

    def get_specialist(self, fio, specialization, department_id, qqc244):
        if entity_exist("244", qqc244):
            spec = self.get_exist_specialist(qqc244=qqc244)
            spec.fio = fio
            spec.specialization = specialization
        else:
            spec = self.cre_spec(fio=fio, specialization=specialization, department_id=department_id, qqc244=qqc244)
        spec.save()
        return spec

    def update_linked_usls(self, qms, specialist, qqc244):
        qms_usls = qms.get_usl_for_spec(qqc244)
        postgre_usls = [du.code for du in specialist.performing_services.all()]
        for usl in qms_usls:
            if usl.code:
                try:
                    if usl.code in postgre_usls:
                        postgre_usls.remove(usl.code)
                    else:
                        usl_obj, created = Service.objects.get_or_create(
                            code=usl.code, clinic=specialist.department.clinic, is_finished=1, level=4,
                        )
                        specialist.performing_services.add(usl_obj)
                except models.ObjectDoesNotExist:
                    continue
        for usl in postgre_usls:
            specialist.performing_services.remove(Service.objects.get(code=usl, clinic=specialist.department.clinic))

    def load_specs_in_department(self, qms, department, qms_department, qms_user):
        qms_specialists = qms.get_all_doctors(qms_department)
        logger.info('Загрузка специалистов из подразделения qms ' + qms_department)
        for spec in qms_specialists:
            if spec.IsActive:
                if spec.firstName and spec.lastName and spec.middleName:
                    fio = spec.firstName + " " + spec.lastName + ' ' + spec.middleName
                    specialization, created = Specialization.objects.get_or_create(name=spec["specialization"])
                    specialist = self.get_specialist(
                        fio=fio, specialization=specialization, department_id=department.id,
                        qqc244=spec.qqc244
                    )
                    specialist.undelete()
                    self.update_linked_usls(qms=qms, specialist=specialist, qqc244=spec.qqc244)
                    specialist.save()

                    # получение основной назначаемой услуги для сервиса записи на прием
                    first_service_code, second_service_code = qms.get_first_and_second_specialist_service_code(
                        get_external_id(specialist, qms_user.qmsdb),
                        qms_user.qqc244
                    )

                    specialist_config, created = SpecialistConfig.objects.get_or_create(
                        specialist=specialist,
                    )

                    if first_service_code:
                        try:
                            first_service = Service.objects.get(
                                clinic=department.clinic,
                                code=first_service_code
                            )
                            specialist_config.service = first_service
                        except Service.DoesNotExist:
                            first_service = None
                            logger.error('Не найдена услуга скодом ' + first_service_code)
                    if second_service_code:
                        try:
                            second_service = Service.objects.get(
                                clinic=department.clinic,
                                code=second_service_code
                            )
                            specialist_config.service2 = second_service
                        except Service.DoesNotExist:
                            second_service = None
                            logger.error('Не найдена услуга скодом ' + second_service_code)

                    specialist_config.save()
            else:
                # если специалист неактивен
                if entity_exist("244", spec.qqc244):
                    specialist = self.get_exist_specialist(spec.qqc244)
                    specialist.safe_delete()

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        try:
            qms_user = qmsdb.qmsuser_set.all()[0]
        except IndexError:
            raise CommandError('Не настроен пользователь Qms для базы ' + dbname)

        department_id = options["department"]
        if department_id:
            departments = Department.objects.filter(id=department_id)
            if not len(departments):
                raise CommandError("Нет подразделения с id = " + department_id)
        else:
            departments = Department.objects.filter(clinic_id=qmsdb.clinic.id)
        logger.info('Загрузка специалистов для учреждения ' + str(qmsdb.clinic))
        qms = QMS(qmsdb.settings)

        for department in departments:
            try:
                qms_department = department.qmsdepartment
            except QmsDepartment.DoesNotExist:
                raise ImproperlyConfigured('Необходимо настроить соответсвие подразделений сайта и qms')
            logger.info('Загрузка специалистов подразделения ' + str(department))
            for qms_department_code in qms_department.codes.all():
                self.load_specs_in_department(qms, department, qms_department_code.code, qms_user)



