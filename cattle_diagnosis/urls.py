from django.contrib import admin
from django.urls import path, include
from diagnosis.views import diagnosis_home, predict_disease
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('diagnosis/', include('diagnosis.urls')),
    path("diagnosis/", diagnosis_home, name="diagnosis_home"),
    path("predict/", predict_disease, name="predict"),
]