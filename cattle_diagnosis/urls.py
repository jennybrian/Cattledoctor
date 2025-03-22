from django.contrib import admin
from django.urls import path, include
from diagnosis.views import diagnosis_home, predict_disease
from accounts.views import home

# Define URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", diagnosis_home, name="home"),  # Root URL shows diagnosis form
    path("diagnosis/", diagnosis_home, name="diagnosis_home"),  # Diagnosis page
    path("predict/", predict_disease, name="predict"),  # API endpoint for predictions
    
    # ✅ Include authentication URLs
    path("accounts/", include("django.contrib.auth.urls")),  # Login, Logout, Password Reset
    path("accounts/", include("accounts.urls")),  # If you have custom user views

    # ✅ Include diagnosis app URLs correctly
    path("diagnosis/", include("diagnosis.urls")),
]