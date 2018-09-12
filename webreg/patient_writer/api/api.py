from django.db.models import Q
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from main.mixins import ProfileRequiredMixinForApi
from main.logic import *
from patient_writer.models import SpecializationConfig
from patient_writer.logic import get_allowed_slot_types


class SpecializationConfigSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.specialization.id

    def get_name(self, obj):
        return obj.specialization.name

    class Meta:
        model = SpecializationConfig
        fields = ('id', 'name', 'enable', 'is_show_comment', 'comment')


class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ('id', 'fio',)


class AvailableSpecializaionsForDepartment(ProfileRequiredMixinForApi, APIView):
    def get(self, request, department_id):
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist as e:
            return Response({"Error": str(e)})
        try:
            patient_id = request.session.get('patient_id', None)
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist as e:
            return Response({"Error": str(e)})

        user_profile = request.user_profile
        specialization_configs = SpecializationConfig.objects.filter(department_config=department.departmentconfig)
        date_from, date_to = department.departmentconfig.get_date_range()
        for specialization_config in specialization_configs:
            allowed_slot_types = get_allowed_slot_types(user_profile, patient,
                                                        department, specialization_config.specialization)
            # проверка наличия свобоных ячеек
            cell_exists = Cell.objects.filter(
                date__range=(date_from, date_to),
                specialist__department_id=department_id,
                specialist__specialization=specialization_config.specialization,
                slot_type__in=allowed_slot_types,
                free=True
            ).exists()
            # настройка показывать комментарий заставляет показывать специальность
            # даже если нет свободных ячеек и специализация выключена
            if not specialization_config.is_show_comment:
                if not specialization_config.enable or \
                   not cell_exists:
                    specialization_configs = specialization_configs.exclude(id=specialization_config.id)

        return Response(SpecializationConfigSerializer(specialization_configs, many=True).data)


class AvailableSpecialists(ProfileRequiredMixinForApi, APIView):
    def get(self, request, **kwargs):
        try:
            patient = Patient.objects.get(id=request.session['patient_id'])
        except (KeyError, Patient.DoesNotExist) as e:
            return Response({"Error": str(e)})

        user_profile = request.user_profile
        department_id = kwargs.get('department_id', None)
        specilization_id = kwargs.get('specialization_id', None)

        # Если есть уже назначения специалистов не выдавать, а просто сообщение

        existing_appointment = Appointment.objects.filter(
            patient=patient,
            date__gte=datetime.datetime.today().date(),
            specialist__specialization_id=specilization_id
        ).first()
        if existing_appointment:
            return Response({"Message": "Вы уже записаны на " + existing_appointment.date.strftime('%d.%m.%Y') +
                             " " + existing_appointment.cell.time_start.strftime("%H:%M") +
                             ". Врач: " + existing_appointment.specialist.fio})
        try:
            specialization = Specialization.objects.get(id=specilization_id)
        except Specialization.DoesNotExist as e:
            return Response({"Error": str(e)})

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist as e:
            return Response({"Error": str(e)})

        allowed_slot_types = get_allowed_slot_types(user_profile, patient, department, specialization)
        specialists = user_profile.get_allowed_specialists(Specialist.objects.filter(
            department=department,
            specialization=specialization
        ))
        date_from, date_to = department.departmentconfig.get_date_range()
        # проверка на доступные для записи ячейки
        for specialist in specialists:
            cell_exists = Cell.objects.filter(
                date__range=(date_from, date_to),
                specialist_id=specialist.id,
                slot_type__in=allowed_slot_types,
                free=True,
            ).exists()
            if not cell_exists:
                specialists = specialists.exclude(id=specialist.id)
        return Response(SpecialistSerializer(specialists, many=True).data)
