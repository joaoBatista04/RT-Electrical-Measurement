from django.db import models

# Create your models here.
class EnergyMeasurement(models.Model):
    timestamp = models.DateTimeField(auto_now_add=False)
    voltage = models.FloatField(null=True, blank=True)
    current = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Measurement at {self.timestamp} - Voltage: {self.voltage}, Current: {self.current}"
