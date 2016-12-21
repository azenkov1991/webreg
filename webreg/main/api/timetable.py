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
    def get(self, request, specialist_id, date_from, date_to):
        specialist_id = int(specialist_id)
        user_profile = request.user_profile
        slot_types = user_profile.get_slot_restrictions().values('id')
        cells = Cell.objects.filter(date__range=(date_from, date_to),
                                    specialist_id=specialist_id)
        if slot_types:
            cells = cells.filter(slot_type__in=slot_types)
        return Response(CellSerializer(cells, many=True).data)
