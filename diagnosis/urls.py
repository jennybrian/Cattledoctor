from django.urls import path
from .views import predict_disease, diagnosis_home
from .views import register, user_login, user_logout, home

# Define URL patterns for the diagnosis app
urlpatterns = [
    path('', diagnosis_home, name='home'),
    path('diagnosis/', diagnosis_home, name='diagnosis_home'),
    path('predict/', predict_disease, name='predict_disease'),
]