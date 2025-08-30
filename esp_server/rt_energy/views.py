from django.shortcuts import render
from django.db.models import Max
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EnergyMeasurement, RMSMeasurement, LastFFT
from .serializers import EnergyMeasurementSerializer, RMSMeasurementSerializer, LastFFTSerializer

from datetime import datetime, timedelta

import threading
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, detrend
from scipy.interpolate import interp1d

def process_esp_async(data):
    final_ts = data.get('timestamp')
    lm358_list = data.get('lm358', [])
    sct013_list = data.get('sct013', [])

    if not final_ts or not isinstance(lm358_list, list) or not isinstance(sct013_list, list):
        raise ValueError("Invalid data format")

    # Converting ADC Value to real voltage/current
    ADC_BITS = 12
    VREF = 3.3
    RBURDEN = 33.0
    CT_RATIO = 2000.0
    K_V = 635.0 # Voltage scaling factor

    scale = VREF / ((1 << ADC_BITS))
    sct013_list = [v * scale for v in sct013_list]
    sct013_mean = sum(sct013_list) / len(sct013_list)
    sct013_list = [(v - sct013_mean) * CT_RATIO / (RBURDEN * 5) for v in sct013_list]  # Remove DC component

    lm358_list = [v * scale for v in lm358_list]
    lm358_mean = sum(lm358_list) / len(lm358_list)
    lm358_list = [(v - lm358_mean) * K_V for v in lm358_list]  # Remove DC component

    final_ts = datetime.fromisoformat(final_ts.replace('Z', '+00:00'))

    total_samples = max(len(lm358_list), len(sct013_list))
    # interval could also be provided in the request
    interval = timedelta(milliseconds=2)  # 2 ms interval between samples (500Hz)
    
    # Voltage is always sinusoidal, so we can use the simplified RMS formula
    if lm358_list:
        squared_sum = sum(i ** 2 for i in lm358_list if i is not None)
        count = sum(1 for i in lm358_list if i is not None)
        v_rms = (squared_sum / count) ** 0.5 if count > 0 else None
    else:
        v_rms = None

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
        measurements = EnergyMeasurement.objects.filter(batch_id=latest_batch).order_by('timestamp')[700:750]
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

        # Recuperar todas as medições da última hora
        agora = timezone.now()
        uma_hora_atras = agora - timedelta(hours=1)
        medidas = RMSMeasurement.objects.filter(timestamp__gte=uma_hora_atras).order_by("timestamp")

        energia_Wh = 0.0

        if medidas.exists():
            for i in range(len(medidas) - 1):
                m1 = medidas[i]
                m2 = medidas[i + 1]

                # Tempo entre medições em segundos
                delta_t = (m2.timestamp - m1.timestamp).total_seconds()

                # Potência média nesse intervalo (em Watts)
                p_med = m1.w_rms if m1.w_rms else 0

                # Energia acumulada (Wh)
                energia_Wh += p_med * (delta_t / 3600.0)

            # Considerar o último ponto até "agora"
            ultimo = medidas.last()
            delta_t = (agora - ultimo.timestamp).total_seconds()
            if ultimo.w_rms:
                energia_Wh += ultimo.w_rms * (delta_t / 3600.0)

        # Serializar última medição
        serializer = RMSMeasurementSerializer(latest_rms)

        # Adicionar a estimativa de energia na response
        response_data = serializer.data
        response_data["energy_hour"] = round(energia_Wh, 3)

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_fft(request):
    """
    Retrieve the FFT of the latest batch of energy measurements.
    Frequencies - Amplitudes - Shift
    """
    try:
        cutoff_hp = 60.0
        order = 4
        f0 = 60

        latest_batch = EnergyMeasurement.objects.aggregate(Max("batch_id"))["batch_id__max"]
        # Get subset of measurements for better performance
        # Remove some samples from start and end due to inconsistencies with the sensors
        measurements = EnergyMeasurement.objects.filter(batch_id=latest_batch).order_by('timestamp')

        df = pd.DataFrame(list(measurements.values('timestamp', 'voltage', 'current')))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['current'] = df['current'].fillna(0)
        df['voltage'] = df['voltage'].fillna(0)

        #Cálculo do tempo de medição e frequência
        t = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds().values
        N = len(t)
        dt = np.mean(np.diff(t))
        fs = 1 / dt

        #Interpolação para garantir uniformidade
        t_uniform = np.linspace(t[0], t[-1], N)
        voltage = interp1d(t, df['voltage'].astype(float), kind='linear')(t_uniform)
        current = interp1d(t, df['current'].astype(float), kind='linear')(t_uniform)

        #Remoção do componente DC (REMOVER ?)
        #voltage = detrend(voltage, type='constant')
        #current = detrend(current, type='constant')

        #Filtro passa-altas para eliminar componentes abaixo da frequência de cutoff definida
        nyq = fs / 2
        Wn = cutoff_hp / nyq
        b, a = butter(order, Wn, btype='high')
        voltage_filt = filtfilt(b, a, voltage)
        current_filt = filtfilt(b, a, current)

        #Normalização da corrente em relação à tensão (DESCOMENTAR CASO QUEIRA NORMALIZAR)
        current_filt = current_filt * (np.max(np.abs(voltage_filt)) / np.max(np.abs(current_filt)))

        #Cálculo da FFT
        fft_v = np.fft.fft(voltage_filt)
        fft_i = np.fft.fft(current_filt)
        freqs = np.fft.fftfreq(N, d=1/fs)

        #Obtenção do ângulo de defasagem na frequência fundamental
        idx = np.argmin(np.abs(freqs - f0))
        phase_v = np.angle(fft_v[idx])
        phase_i = np.angle(fft_i[idx])
        phase_diff_rad = (phase_i - phase_v + np.pi) % (2*np.pi) - np.pi
        phase_diff_deg = np.degrees(phase_diff_rad)

        #Normalização do ângulo
        phase_diff_deg = (phase_diff_deg + 180) % 360 - 180
        if phase_diff_deg > 90:
            phase_diff_deg -= 180
        elif phase_diff_deg < -90:
            phase_diff_deg += 180

        response = [
            {"frequency": freqs[i], "amplitude": abs(fft_i[i]) if fft_i[i] else 0} for i in range(len(freqs)) if freqs[i] > 50 and freqs[i] % 5 == 0
        ]

        LastFFT.objects.all().delete()
        LastFFT.objects.create(data=response, phase_diff_deg=phase_diff_deg)

        print(phase_diff_deg)
        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_phase_angle(request):
    """
    Retrieve the phase angle between voltage and current.
    """
    try:
        last_fft = LastFFT.objects.latest("id")

        load_type = "Resistiva"
        if last_fft.phase_diff_deg > 20:
            load_type = "Indutiva"
        elif last_fft.phase_diff_deg < -20:
            load_type = "Capacitiva"

        return Response({"phase_angle": last_fft.phase_diff_deg, "type": load_type}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)