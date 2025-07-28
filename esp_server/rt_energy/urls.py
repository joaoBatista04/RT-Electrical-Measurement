from django.urls import path
from .views import esp_data_upload

urlpatterns = [
    path('upload/', esp_data_upload, name='esp_data_upload'),
]