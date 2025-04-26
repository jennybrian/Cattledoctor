from django.urls import path
from .views import predict_disease, diagnosis_home

# Define URL patterns for the diagnosis app
urlpatterns = [
    path('diagnosis/', diagnosis_home, name='diagnosis_home'),
    path('predict/', predict_disease, name='predict_disease'),
]