from django.shortcuts import render
from django.db.models import Max
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EnergyMeasurement, RMSMeasurement
from .serializers import EnergyMeasurementSerializer, RMSMeasurementSerializer

from datetime import datetime, timedelta

import threading
import numpy as np

def process_esp_async(data):
    final_ts = data.get('timestamp')
    lm358_list = data.get('lm358', [])
    sct013_list = data.get('sct013', [])

    if not final_ts or not isinstance(lm358_list, list) or not isinstance(sct013_list, list):
        raise ValueError("Invalid data format")

    # Converting ADC Value to real voltage/current
    ADC_BITS = 12
    VREF = 3.1
    RBURDEN = 33.0
    CT_RATIO = 2000.0
    K_V = 635.0 # Voltage scaling factor

    scale = VREF / ((1 << ADC_BITS) - 1)
    sct013_list = [v * scale for v in sct013_list]
    sct013_mean = sum(sct013_list) / len(sct013_list)
    sct013_list = [(v - sct013_mean) * CT_RATIO / RBURDEN for v in sct013_list]  # Remove DC component

    lm358_list = [v * scale for v in lm358_list]
    lm358_mean = sum(lm358_list) / len(lm358_list)
    lm358_list = [(v - lm358_mean) * K_V for v in lm358_list]  # Remove DC component

    final_ts = datetime.fromisoformat(final_ts.replace('Z', '+00:00'))

    total_samples = max(len(lm358_list), len(sct013_list))
    # interval could also be provided in the request
    interval = timedelta(milliseconds=2)  # 2 ms interval between samples (500Hz)
    
    # Voltage is always sinusoidal, so we can use the simplified RMS formula
    v_rms = max(lm358_list) * 0.707 if lm358_list else None

    # Current can be non-sinusoidal, so we calculate the RMS value normally
    if sct013_list:
        squared_sum = sum(i ** 2 for i in sct013_list if i is not None)
        count = sum(1 for i in sct013_list if i is not None)
        i_rms = (squared_sum / count) ** 0.5 if count > 0 else None
    else:
        i_rms = None

    # Save RMSMeasurement 

    RMSMeasurement.objects.create(timestamp=final_ts, v_rms=v_rms, i_rms=i_rms, w_rms=(v_rms * i_rms) if v_rms and i_rms else None)

    # --- Gerenciar lotes ---
    # Descobrir último batch_id usado
    last_batch = EnergyMeasurement.objects.aggregate(Max("batch_id"))["batch_id__max"] or 0
    new_batch_id = last_batch + 1

    objects = []
    print(total_samples, interval)
    for i in range(total_samples):
        timestamp = final_ts - (total_samples - i - 1) * interval
        voltage = lm358_list[i] if i < len(lm358_list) else None
        current = sct013_list[i] if i < len(sct013_list) else None

        measurement = EnergyMeasurement(timestamp=timestamp, 
                                        voltage=voltage, 
                                        current=current, 
                                        batch_id=new_batch_id)
        
        #print(f"Creating measurement: {measurement}")
        objects.append(measurement)

    # Se já temos >= 4 lotes, apagar o mais antigo
    distinct_batches = EnergyMeasurement.objects.values_list("batch_id", flat=True).distinct().order_by("batch_id")
    if distinct_batches.count() >= 4:
        oldest = distinct_batches.first()
        EnergyMeasurement.objects.filter(batch_id=oldest).delete()

    EnergyMeasurement.objects.bulk_create(objects)

@api_view(['POST'])
def esp_data_upload(request):
    """
    Handle POST requests from ESP devices.
    """
    try:
        data = request.data
        
        threading.Thread(target=process_esp_async, args=(data,), daemon=True).start()

        return Response({"message": "Data uploaded successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_latest_measurements(request):
    """
    Retrieve the latest batch of energy measurements.
    """
    try:
        latest_batch = EnergyMeasurement.objects.aggregate(Max("batch_id"))["batch_id__max"]
        measurements = EnergyMeasurement.objects.filter(batch_id=latest_batch).order_by('timestamp')[100:200]
        serializer = EnergyMeasurementSerializer(measurements, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_latest_rms(request):
    """
    Retrieve the latest RMS measurement.
    """
    try:
        latest_rms = RMSMeasurement.objects.latest("timestamp")
        serializer = RMSMeasurementSerializer(latest_rms)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_fft(request):
    """
    Retrieve the FFT of the latest batch of energy measurements.
    Frequencies - Amplitudes - Shift
    """
    try:
        latest_batch = EnergyMeasurement.objects.aggregate(Max("batch_id"))["batch_id__max"]
        # Get subset of measurements for better performance
        measurements = EnergyMeasurement.objects.filter(batch_id=latest_batch).order_by('timestamp')

        voltages = [m.voltage for m in measurements if m.voltage is not None]
        currents = [m.current for m in measurements if m.current is not None]

        fs = 500  # Sample frequency (500Hz)

        # FFT
        fft_v = np.fft.fft(voltages)
        fft_i = np.fft.fft(currents)

        freqs = np.fft.fftfreq(len(currents), d=1/fs)

        # Get only positive frequencies
        pos_mask = freqs > 0
        freqs = freqs[pos_mask]
        fft_v = np.abs(fft_v[pos_mask])
        fft_i = np.abs(fft_i[pos_mask])

        response = [
            {"frequency": freqs[i], "amplitude": fft_i[i]} for i in range(len(freqs))
        ]

        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)