from django.contrib import admin
from django.urls import path, include
from accounts.views import home, verify_email

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('verify-email/<str:token>/', verify_email, name='verify_email'),
    path('diagnosis/', include('diagnosis.urls')),
]