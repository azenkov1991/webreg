import  logging
from catalogs.models import *
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from main.models import Specialist, Department, Specialization

logger = logging.getLogger("webreg")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("department", help="Id подразделения", type=int)

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
                        usl_obj, created = OKMUService.objects.get_or_create(code=usl.code, is_finished=1, level=4)
                        specialist.performing_services.add(usl_obj)
                except models.ObjectDoesNotExist:
                    continue
        for usl in postgre_usls:
            specialist.performing_services.remove(OKMUService.objects.get(code=usl))

    def load_specs_in_department(self, qms, department, qms_department):
        qms_specialists = qms.get_all_doctors(qms_department)
        for spec in qms_specialists:
            if spec.IsActive:
                if spec.firstName and spec.lastName and spec.middleName:
                    fio = spec.firstName + " " + spec.lastName + ' ' + spec.middleName
                    specialization, created = Specialization.objects.get_or_create(name=spec["specialization"])
                    specialist = self.get_specialist(fio=fio, specialization=specialization, department_id=department.id,
                                                     qqc244=spec.qqc244)
                    specialist.undelete()
                    self.update_linked_usls(qms=qms, specialist=specialist, qqc244=spec.qqc244)
                    specialist.save()
            else:
                if entity_exist("244", spec.qqc244):
                    specialist = self.get_exist_specialist(spec.qqc244)
                    specialist.safe_delete()

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        department_id = options["department"]
        try:
            department = Department.objects.get(pk=department_id)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет подразделения с id = " + department_id)


        qms = QMS(qmsdb.settings)
        try:
            qms_department = department.qmsdepartment
        except QmsDepartment.DoesNotExist:
            raise ImproperlyConfigured('Необходимо настроить соответсвие подразделений сайта и qms')

        for qms_department_code in qms_department.codes.all():
            self.load_specs_in_department(qms, department, qms_department_code.code)



