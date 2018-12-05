from django.core.management.base import BaseCommand, CommandError
from django.db import models
from main.models import Department, Specialization, SlotType, Service
from patient_writer.models import DepartmentConfig, SpecializationConfig, SlotTypeConfig
from qmsintegration.models import QmsDepartment, QmsDepartmentCode


class DepartmentOld(models.Model):

    name = models.CharField(
        max_length=255, verbose_name='Название департамента'
    )
    address = models.CharField(
        max_length=255, verbose_name='Адрес департамента'
    )
    mobile_name = models.CharField(
        max_length=255, verbose_name="Мобильное имя", blank=True, null=True
    )
    city_id = models.IntegerField(
        verbose_name='Город', db_column='city_id'
    )
    day_start_offset = models.PositiveIntegerField(
        default=1, verbose_name='Отступ начала записи'
    )
    today_time_interval = models.PositiveIntegerField(
        default=60, verbose_name='Защитный интервал записи в текущий день',
        help_text='Минуты'
    )
    day_range = models.PositiveIntegerField(
        default=0, verbose_name='Период записи'
    )
    day_range_previousqqc174 = models.PositiveIntegerField(
        default=0, verbose_name='Период просмотра существующего эпизода'
    )
    type_incoming = models.CharField(
        max_length=63, verbose_name='Тип поступления'
    )
    phone = models.CharField(
        max_length=31, verbose_name='Телефон для отказов', blank=True, null=True
    )
    phone2 = models.CharField(
        max_length=31, verbose_name='Телефон для информирования', blank=True, null=True
    )
    min_age = models.PositiveIntegerField(
        default=0, verbose_name='Минимальный возраст'
    )
    max_age = models.PositiveIntegerField(
        default=0, verbose_name='Максимальный возраст'
    )
    is_active = models.BooleanField(
        default=True, verbose_name='Включить'
    )

    permament_disable = models.BooleanField(
        default=False, verbose_name='Выключить навсегла'
    )

    is_show_comment = models.BooleanField(default=False, verbose_name='Вывод комментария')
    comment = models.CharField(max_length=512, verbose_name='Комментарий', blank=True, null=True)

    class Meta:
        managed = False
        db_table = "patient_writer_departament"


class DepartamentCodeOld(models.Model):
    departament_id = models.IntegerField(verbose_name='Департамент')
    code = models.CharField(max_length=31, verbose_name='Код')
    is_active_write = models.BooleanField(verbose_name='Доступность для записи', default=True)

    class Meta:
        managed = False
        db_table = "patient_writer_departamentcode"


class SessionTypeOld(models.Model):
    name = models.CharField(max_length=31, verbose_name='Тип', default='')
    min_age = models.PositiveIntegerField(default=0, verbose_name='Минимальный возраст')
    max_age = models.PositiveIntegerField(default=0, verbose_name='Максимальный возраст')

    class Meta:
        managed = False
        db_table = "patient_writer_sessiontype"


class SpecialityOldSessionTypeOld(models.Model):
    session_type_id = models.IntegerField(
        db_column='sessiontype_id'
    )
    speciality_id = models.IntegerField(
        db_column='speciality_id'
    )

    class Meta:
        managed = False
        db_table = "patient_writer_speciality_session_types"


class SpecialityOld(models.Model):
    departament = models.ForeignKey(
        DepartmentOld, verbose_name='Департамент', related_name='specialities'
    )
    name = models.CharField(max_length=31, verbose_name='Название специальности')
    re_name = models.CharField(max_length=127, verbose_name='Название специальности для RE')
    is_area_constrain = models.BooleanField(default=False, verbose_name='Ограничение по участку')
    is_get_doctor = models.BooleanField(default=True, verbose_name='Поиск докторов')
    is_show_comment = models.BooleanField(default=False, verbose_name='Вывод комментария')
    comment = models.CharField(max_length=512, verbose_name='Комментарий', blank=True, null=True)

    class Meta:
        managed = False
        db_table = "patient_writer_speciality"


class DoctorOld(models.Model):
    departament = models.ForeignKey(DepartmentOld, verbose_name='Департамент', related_name='doctors')
    qqc244 = models.CharField(max_length=63, verbose_name='qqc244')
    name = models.CharField(max_length=127, verbose_name='Имя')
    staff = models.CharField(max_length=127, verbose_name='Должность')
    usl_du = models.CharField(max_length=63, verbose_name='Код услуги')
    usl_du2 = models.CharField(max_length=63, verbose_name='Код услуги повторного приема')
    is_active = models.BooleanField(default=True, verbose_name='Активен?')

    class Meta:
        managed = False
        db_table = "patient_writer_doctor"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('clinic_id', type=int, help='Id медучереждения')
        parser.add_argument('city_id', type=int, help="Id города в старом сервисе")

    def handle(self, *args, **options):
        clinic_id = options['clinic_id']
        city_id = options['city_id']

        departments_from_old_site =  DepartmentOld.objects.using('old_db').filter(city_id=city_id)

        for old_dep in departments_from_old_site:
            department = Department(
                name=old_dep.name,
                clinic_id=clinic_id,
                address=old_dep.address
            )
            department.save()
            print('Создано подразделение: ' + str(department))

            department_config = DepartmentConfig(
                department_id=department.id,
                day_start_offset=old_dep.day_start_offset,
                today_time_interval=old_dep.today_time_interval,
                day_range=old_dep.day_range,
                phone=old_dep.phone,
                phone2=old_dep.phone2,
                order=old_dep.id,
                min_age=old_dep.min_age,
                max_age=old_dep.max_age,
            )
            department_config.save()
            print('Созданы настройки для подразделения ' + str(department))
            episode_type = 1 if old_dep.type_incoming == "АМБУЛАТОРНО" else 2
            qms_department = QmsDepartment(department=department, episode_type=episode_type)
            qms_department.save()
            print('Создано qms подразделение для ' + str(department))

            dep_codes_old = DepartamentCodeOld.objects.using('old_db').filter(departament_id=old_dep.id)

            for dep_code_old in dep_codes_old:
                qms_department_code = QmsDepartmentCode(
                    qmsdepartament=qms_department, code=dep_code_old.code
                )
                qms_department_code.save()
                print('Добавлен код подразделения qms' + dep_code_old.code + 'для ' + str(department))

            for old_spec in SpecialityOld.objects.using('old_db').filter(
                departament_id=old_dep.id, is_get_doctor=True
            ):
                try:
                    specialization = Specialization.objects.filter(name__iexact=old_spec.name)[0]
                    print('Найдена специализация ' + specialization.name)

                except IndexError:
                    specialization = Specialization(
                        name=(old_spec.name[0].upper() + old_spec.name[1:].lower())
                    )
                    specialization.save()
                    print('не найдена специализация ' + old_spec.name)

                old_doctors = DoctorOld.objects.using('old_db').filter(
                    departament_id=old_dep.id,
                    staff__contains=old_spec.name
                ).values('usl_du').annotate(du_count=models.Count('usl_du')).order_by('-du_count')
                if not old_doctors:
                    continue
                service_code = old_doctors[0]['usl_du']

                try:
                    service = Service.objects.get(
                        code=service_code,
                        clinic_id=clinic_id
                    )
                except Service.DoesNotExist:
                    continue

                specialization_config = SpecializationConfig(
                    specialization_id=specialization.id,
                    department_config_id=department_config.id,
                    service=service,
                    is_show_comment=old_spec.is_show_comment,
                    comment=old_spec.comment
                )

                specialization_config.save()

                session_type_ids = list(SpecialityOldSessionTypeOld.objects.using('old_db').filter(
                    speciality_id=old_spec.id
                ).values_list('session_type_id', flat=True))
                print(session_type_ids)
                session_types_names = SessionTypeOld.objects.using('old_db').filter(
                    id__in=session_type_ids,
                ).values_list('name', flat=True)
                print(session_types_names)
                for session_type_name in session_types_names:
                    try:
                        slot_type = SlotType.objects.get(
                            name=session_type_name,
                            clinic_id=clinic_id,
                        )
                        specialization_config.slot_types.add(slot_type)
                        print("Для")
                    except SlotType.DoesNotExist:
                        pass





