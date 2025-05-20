from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', account_views.register, name='register'),
    path('', include('diagnosis.urls')),  # Include diagnosis URLs at root
]