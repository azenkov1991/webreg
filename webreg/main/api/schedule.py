from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
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
        specialist_id = int(specialist_id)
        site = get_current_site(request)
        user_profile = UserProfile.get(site_id=site.id, user_id=request.user.id)
        slot_types = user_profile.get_slot_restriction().values('id')
        if slot_types:
            cells = Cell.objects.filter(date__range=(date_from, date_to),
                                        specialist_id=specialist_id,
                                        slot_type__in=slot_types)
        else:
            cells = Cell.objects.filter(date__range=(date_from, date_to),
                                        specialist_id=specialist_id)
        return Response(CellSerializer(cells).data)








