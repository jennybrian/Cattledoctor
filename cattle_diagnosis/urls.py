from django.contrib import admin
from django.urls import path, include
from diagnosis.views import diagnosis_home, predict_disease
from accounts.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),  # Changed: Root URL now shows landing page
    path("diagnosis/", include("diagnosis.urls")),  # Keep diagnosis URLs
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
]