from django.urls import path
from .views import predict_disease, diagnosis_home

urlpatterns = [
    path('diagnosis/', diagnosis_home, name='diagnosis_home'),
    path('predict/', predict_disease, name='predict_disease'),
]
