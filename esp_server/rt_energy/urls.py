from django.urls import path
from .views import esp_data_upload, get_latest_measurements, get_latest_rms, get_fft, get_phase_angle

urlpatterns = [
    path('upload/', esp_data_upload, name='esp_data_upload'),
    path('latest_batch/', get_latest_measurements, name='latest_batch'),
    path('latest_rms/', get_latest_rms, name='latest_rms'),
    path('get_fft/', get_fft, name='get_fft'),
    path('get_phase_angle/', get_phase_angle, name='get_phase_angle')
]
