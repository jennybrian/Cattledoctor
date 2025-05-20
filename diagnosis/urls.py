from django.urls import path
from . import views

urlpatterns = [
    path('diagnosis/', views.diagnosis_home, name='diagnosis_home'),
    path('predict/', views.predict_disease, name='predict_disease'),
    path('history/', views.diagnosis_history, name='diagnosis_history'),
    path('history/clear/', views.clear_history, name='clear_history'),
    path('history/mark-resolved/<int:history_id>/', views.mark_resolved, name='mark_resolved'),
    path('history/export-pdf/', views.export_pdf, name='export_pdf'),
]
