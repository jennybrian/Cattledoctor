from django.urls import path
from .views import predict_disease, diagnosis_home

urlpatterns = [
    # Remove the root path that conflicts with main home view
    path('diagnosis/', diagnosis_home, name='diagnosis_home'),  # Keep only this for diagnosis
    path('predict/', predict_disease, name='predict_disease'),
]