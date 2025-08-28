from django.db import models

# Create your models here.
class EnergyMeasurement(models.Model):
    timestamp = models.DateTimeField(auto_now_add=False)
    voltage = models.FloatField(null=True, blank=True)
    current = models.FloatField(null=True, blank=True)
    batch_id = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return f"Measurement at {self.timestamp} - Voltage: {self.voltage}, Current: {self.current}"

class RMSMeasurement(models.Model):
    timestamp = models.DateTimeField(auto_now_add=False)
    v_rms = models.FloatField(null=True, blank=True)
    i_rms = models.FloatField(null=True, blank=True)
    w_rms = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"RMS Measurement at {self.timestamp} - V_RMS: {self.v_rms}, I_RMS: {self.i_rms}"
    
class LastFFT(models.Model):
    data = models.JSONField(null=False, blank=False)
    phase_diff_deg = models.FloatField(null=True, blank=True)
    

    def __str__(self):
        return f"Last FFT Measurement - Phase Difference: {self.phase_diff_deg}"