from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from main.mixins import ProfileRequiredMixin

from main.models import *


class CabinetTimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        fields = ('id', 'number', 'name')


class SlotTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlotType
        fields = ('id', 'color', 'name')


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'fio', 'birth_date')


class CellSerializer(serializers.ModelSerializer):
    cabinet = CabinetTimeTableSerializer()
    slot_type = SlotTypeSerializer()

    class Meta:
        model = Cell
        fields = ('id', 'date', 'time_start', 'time_end', 'cabinet', 'slot_type')


class SpecialistsFreeCells(ProfileRequiredMixin, APIView):
    """
    Возвращает свободные ячейки специалиста
    """
    def get(self, request, specialist_id, date_from, date_to, slot_type_id=""):
        specialist_id = int(specialist_id)
        user_profile = request.user_profile
        slot_types = user_profile.get_slot_restrictions().values('id')
        cells = Cell.objects.filter(date__range=(date_from, date_to),
                                    specialist_id=specialist_id,
                                    appointment__isnull=True)
        if slot_type_id:
            cells = cells.filter(slot_type_id=int(slot_type_id))
        if slot_types:
            cells = cells.filter(slot_type_id__in=slot_types)
        return Response(CellSerializer(cells, many=True).data)


class SpecialistAllCells(ProfileRequiredMixin, APIView):
    """
    Возвращает все ячейки расписания с информацией о назначенном пациенте
    """
    def get(self, request, specialist_id, date_from, date_to):
        specialist_id = int(specialist_id)
        cells = Cell.objects.filter(date__range=(date_from, date_to),
                                    specialist_id=specialist_id)

        cells_list = CellSerializer(cells, many=True).data
        for i, value in enumerate(cells_list):
            try:
                appointment = Appointment.objects.get(cell_id=int(value['id']))
                print (value['id'])
                cells_list[i]['patient'] = PatientSerializer(appointment.patient).data
            except Appointment.DoesNotExist:
                pass
        return Response(cells_list)


