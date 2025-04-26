from django.urls import path
from .views import predict_disease, diagnosis_home

# Define URL patterns for the diagnosis app
urlpatterns = [
    # Remove duplicate root path since it's handled by main urls.py
    path('diagnose/', diagnosis_home, name='diagnosis_home'),  # Changed path for clarity
    path('predict/', predict_disease, name='predict_disease'),
]