from django.urls import path
from .views import predict_disease, diagnosis_home, diagnosis_history, clear_history
from . import views

urlpatterns = [
    path('diagnosis/', diagnosis_home, name='diagnosis_home'),
    path('predict/', predict_disease, name='predict_disease'),
    path('diagnosis-history/', diagnosis_history, name='diagnosis_history'),
    path('history/clear/', clear_history, name='clear_history'),
    path('mark-resolved/<int:history_id>/', views.mark_resolved, name='mark_resolved')
]
