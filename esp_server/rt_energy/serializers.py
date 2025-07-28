from rest_framework import serializers
from .models import EnergyMeasurement

class EnergyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyMeasurement
        fields = '__all__'