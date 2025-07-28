from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EnergyMeasurement
from .serializers import EnergyMeasurementSerializer

from datetime import datetime, timedelta

@api_view(['POST'])
def esp_data_upload(request):
    """
    Handle POST requests from ESP devices.
    """
    try:
        data = request.data
        final_ts = data.get('timestamp')
        lm358_list = data.get('lm358', [])
        sct013_list = data.get('sct013', [])

        if not final_ts or not isinstance(lm358_list, list) or not isinstance(sct013_list, list):
            return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

        final_ts = datetime.fromisoformat(final_ts.replace('Z', '+00:00'))

        total_samples = max(len(lm358_list), len(sct013_list))
        # interval could also be provided in the request
        interval = timedelta(milliseconds=8)  # 8 ms interval between samples (120Hz)

        objects = []

        for i in range(total_samples):
            timestamp = final_ts - (total_samples - i - 1) * interval
            voltage = lm358_list[i] if i < len(lm358_list) else None
            current = sct013_list[i] if i < len(sct013_list) else None

            measurement = EnergyMeasurement(timestamp=timestamp, voltage=voltage, current=current)
            print(f"Creating measurement: {measurement}")
            objects.append(measurement)

        EnergyMeasurement.objects.bulk_create(objects)
        return Response({"message": "Data uploaded successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)