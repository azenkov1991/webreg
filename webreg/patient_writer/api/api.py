from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from main.mixins import ProfileRequiredMixin

from main.logic import *

class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ('id', 'fio',)


class AvailableSpecialist(ProfileRequiredMixin, APIView):
    def get(self, request, department_id=None):
        if department_id:
            specialists=Specialist.objects.filter(department_id=department_id)
        else:
            specialists=Specialist.objects.all()
        user_profile = request.user_profile
        specialists = user_profile.get_allowed_specialists(specialists)
        return Response(SpecialistSerializer(specialists,many=True).data)
