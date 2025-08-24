import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, detrend
from scipy.interpolate import interp1d

def compute_fft_from_json(data, time_col="timestamp", voltage_col="voltage", current_col="current", cutoff_hp=60.0, order=4):
    """
    Processa sinais de tensão e corrente a partir de dados JSON e retorna as FFTs complexas e frequências.
    """

    #Transformar JSON em DataFrame
    df = pd.DataFrame(data)
    df[time_col] = pd.to_datetime(df[time_col])
    
    #Cálculo do tempo de medição e frequência
    t = (df[time_col] - df[time_col].iloc[0]).dt.total_seconds().values
    N = len(t)
    dt = np.mean(np.diff(t))
    fs = 1 / dt
    
    #Interpolação para garantir uniformidade
    t_uniform = np.linspace(t[0], t[-1], N)
    voltage = interp1d(t, df[voltage_col].astype(float), kind='linear')(t_uniform)
    current = interp1d(t, df[current_col].astype(float), kind='linear')(t_uniform)
    
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
    #current_filt = current_filt * (np.max(np.abs(voltage_filt)) / np.max(np.abs(current_filt)))

    #Cálculo da FFT
    V = np.fft.fft(voltage_filt)
    I = np.fft.fft(current_filt)
    freqs = np.fft.fftfreq(N, d=1/fs)
    
    return {
        "fs": fs,
        "t": t_uniform,
        "freqs": freqs,
        "V_fft": V,
        "I_fft": I,
        "voltage_filt": voltage_filt,
        "current_filt": current_filt,
    }

def compute_phase_at_fundamental(V_fft, I_fft, freqs, f0=60.0):
    """
    Calcula a defasagem entre a corrente e a tensão na frequência fundamental (f0).
    Retorna a defasagem em radianos e graus.
    """

    #Obtenção do ângulo de defasagem na frequência fundamental
    idx = np.argmin(np.abs(freqs - f0))
    phase_v = np.angle(V_fft[idx])
    phase_i = np.angle(I_fft[idx])
    phase_diff_rad = (phase_i - phase_v + np.pi) % (2*np.pi) - np.pi
    phase_diff_deg = np.degrees(phase_diff_rad)

    #Normalização do ângulo
    phase_diff_deg = (phase_diff_deg + 180) % 360 - 180
    if phase_diff_deg > 90:
        phase_diff_deg -= 180
    elif phase_diff_deg < -90:
        phase_diff_deg += 180

    if(phase_diff_deg > 5):
        load_type = 'Capacitiva'
    elif(phase_diff_deg < -5):
        load_type = 'Indutiva'
    else:
        load_type = 'Resistiva'

    return {
        "phase_shift": phase_diff_deg,
        "load_type": load_type
    }

def plot_fft(freqs, V_fft, I_fft, base_freq=60.0, max_harmonic=5):
    """
    Plota o espectro (magnitude) da tensão e da corrente até o n-ésimo harmônico.
    """

    N = len(freqs)
    mask = freqs >= 0
    freqs_pos = freqs[mask]
    V_mag = np.abs(V_fft[mask]) / N
    I_mag = np.abs(I_fft[mask]) / N

    plt.figure(figsize=(10, 4))
    plt.plot(freqs_pos, V_mag, label='Tensão (FFT)', linewidth=1.5)
    plt.plot(freqs_pos, I_mag, label='Corrente (FFT)', linewidth=1.5)
    plt.xlim(-5, base_freq * max_harmonic)
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.title(f"Espectro da FFT até o {max_harmonic}º harmônico")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

#============================ MAIN #============================

with open('medidas_aspirador.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

#FFT dos sinais (PARA REMOVER NÍVEL DC DA VISUALIZAÇÃO DA FFT, AJUSTAR CUTOFF PARA 60Hz)
result = compute_fft_from_json(data, cutoff_hp=60)

#Cálculo da defasagem na fundamental
phase_result = compute_phase_at_fundamental(
    result['V_fft'], result['I_fft'], result['freqs'], f0=60
)

#Plotagem da FFT
plot_fft(result['freqs'], result['V_fft'], result['I_fft'], base_freq=60)

#Resultados
print(f"Defasagem da corrente em relação à tensão: {phase_result['phase_shift']:.2f}°")
print(f"Carga {phase_result['load_type']}")
