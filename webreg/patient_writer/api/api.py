from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from main.mixins import ProfileRequiredMixin, ProfileRequiredMixinForApi
from main.logic import *
from patient_writer.models import DepartmentConfig, SpecializationConfig

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


class AvailableSpecializaionForDepartment(ProfileRequiredMixinForApi, APIView):
    def get(self, request, department_id):
        try:
            department_config = DepartmentConfig.objects.get(department_id=department_id)
        except DepartmentConfig.DoesNotExist:
            return Response({})
        specialization_configs = SpecializationConfig.objects.filter(department_config=department_config)

        date_from, date_to = department_config.get_date_range()
        for specialization_config in specialization_configs:
            # проверка наличия свобоных ячеек
            cell_exists = Cell.objects.filter(
                date__range=(date_from, date_to),
                specialist__department_id=department_id,
                specialist__specialization=specialization_config.specialization,
                free=True
            ).exists()
            # настройка показывать комментарий заставляет показывать специальность
            # даже если нет свободных ячеек и специализация выключена
            if not specialization_config.is_show_comment:
                if not specialization_config.enable or \
                   not cell_exists:
                    specialization_configs = specialization_configs.exclude(id=specialization_config.id)

        return Response(SpecializationConfigSerializer(specialization_configs, many=True).data)


class AvailableSpecialist(ProfileRequiredMixinForApi, APIView):
    def get(self, request, **kwargs):
        department_id = kwargs.get('department_id', None)
        specilization_id = kwargs.get('specialization_id', None)
        if department_id:
            specialists = Specialist.objects.filter(department_id=department_id)
        else:
            specialists = Specialist.objects.all()
        if specilization_id:
            specialists = specialists.filter(specialization_id=specilization_id)
        try:
            department_config = DepartmentConfig.objects.get(department_id=department_id)
        except DepartmentConfig.DoesNotExist:
            return Response({})

        user_profile = request.user_profile
        specialists = user_profile.get_allowed_specialists(specialists)
        date_from, date_to = department_config.get_date_range()
        for specialist in specialists:
            cell_exists = Cell.objects.filter(
                date__range=(date_from, date_to),
                specialist_id=specialist.id,
                free=True
            ).exists()
            if not cell_exists:
                specialists = specialists.exclude(id=specialist.id)

        return Response(SpecialistSerializer(specialists, many=True).data)
