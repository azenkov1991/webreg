from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
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
        fields = fields = ('id', 'date', 'time_start', 'time_end', 'cabinet')


class SpecialistsFreeCells(APIView):
    """
    Возвращает свободные ячейки специалиста
    """
    def get(self, request, specialist_id, date_from, date_to):
        pass





