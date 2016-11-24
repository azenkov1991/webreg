import  logging
from catalogs.models import *
from django.core.management.base import BaseCommand, CommandError
from qmsmodule.qmsfunctions import *
from qmsintegration.models import *
from main.models import Specialist, Department, Specialization

logger = logging.getLogger("webreg")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("dbname", help="Название настроек базы QMS из qmsintegration.OmsDB")
        parser.add_argument("pID", help="Подразделение в QMS")
        parser.add_argument("department", help="Id подразделения", type=int)
        parser.add_argument("-d", "--delete", help="Перед загрузкой все специалисты будут удалены",
                            action="store_true", dest="delete")

    def cre_spec(self, fio, specialization, department_id, qqc244, IsActive):
        spec = None
        try:
            spec = Specialist(fio=fio, specialization=specialization, department_id=department_id, IsActive=IsActive)
            spec.save()
            set_external_id(spec, qqc244)
        except Exception as ex:
            logger.error("Не удалось загрузить специалиста из qms " + qqc244 + ' ' + fio + "\n" +
                         str(ex))
        return spec

    def get_exist_specialist(self, qqc244):
        int_id = get_internal_id(qqc244, "244")
        specialist = Specialist.objects.get(pk=int_id)
        return specialist

    def get_specialist(self, fio, specialization, department_id, qqc244, IsActive):
        if entity_exist("244", qqc244):
            spec = self.get_exist_specialist(qqc244=qqc244)
            spec.fio = fio
            spec.specialization = specialization
            spec.IsActive = IsActive
        else:
            spec = self.cre_spec(fio=fio, specialization=specialization, department_id=department_id, qqc244=qqc244, IsActive=IsActive)
        spec.save()
        return spec

    def get_specialization(self, specialization):
        spec2 = specialization.replace('_', ' ')
        try:
            obj = Specialization.objects.get(name__iexact=spec2)
        except models.ObjectDoesNotExist:
            obj = Specialization(name = spec2)
        obj.save()
        return obj

    def get_usl(self, okmu):
        try:
            obj = OKMUService.objects.get(code=okmu)
        except models.ObjectDoesNotExist:
            obj = OKMUService(code=okmu, is_finished=True, level=5)
        obj.save()
        return obj

    def update_linked_usls(self, qms, specialist, qqc244):
        qms_usls = qms.get_usl_for_spec(qqc244)
        postgre_usls = [du.code for du in specialist.performing_services.all()]
        for usl in qms_usls:
            if usl.code:
                try:
                    if usl.code in postgre_usls:
                        postgre_usls.remove(usl.code)
                    else:
                        usl_obj = self.get_usl(usl.code)
                        specialist.performing_services.add(usl_obj)
                except models.ObjectDoesNotExist:
                    continue
        for usl in postgre_usls:
            specialist.performing_services.remove(OKMUService.objects.get(code=usl))

    def handle(self, *args, **options):
        dbname = options["dbname"]
        try:
            qmsdb = QmsDB.objects.get(name=dbname)
        except models.ObjectDoesNotExist:
            raise CommandError("Нет описания базы данных Qms с именем " + dbname)
        try:
            department = Department.objects.get(name=options["pID"])
        except:
            department_id = options["department"]
            try:
                department = Department.objects.get(pk=department_id)
            except models.ObjectDoesNotExist:
                raise CommandError("Нет подразделения с id = " + department_id)
        if options["delete"]:
            specialists = Specialist.objects.filter(department_id=department.id)
            delete_external_ids(specialists)

        qms = QMS(qmsdb.settings)
        qms_specialists = qms.get_all_doctors(department.name)
        postgre_specialists = [spec for spec in Specialist.objects.filter(department=department, IsActive=True)]
        for spec in qms_specialists:
            if spec.IsActive:
                if spec.firstName and spec.lastName and spec.middleName:
                    fio = spec.firstName + " " + spec.lastName + ' ' + spec.middleName
                    specialization = self.get_specialization(spec["specialization"])
                    specialist = self.get_specialist(fio=fio, specialization=specialization, department_id=department.id,
                                                     qqc244=spec.qqc244, IsActive=spec.IsActive)
                    if specialist in postgre_specialists:
                        postgre_specialists.remove(specialist)
                    self.update_linked_usls(qms=qms, specialist=specialist, qqc244=spec.qqc244)
                    specialist.save()
        for spec in postgre_specialists:
            spec.IsActive = False
            spec.save()


