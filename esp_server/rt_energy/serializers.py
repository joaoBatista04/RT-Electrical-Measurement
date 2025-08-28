from rest_framework import serializers
from .models import EnergyMeasurement
from .models import RMSMeasurement
from .models import LastFFT

class EnergyMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyMeasurement
        fields = '__all__'

class RMSMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RMSMeasurement
        fields = '__all__'

class LastFFTSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastFFT
        fields = '__all__'