from django.contrib import admin
from django.urls import path, include
from accounts.views import home  # Import home view from accounts

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Root URL shows landing page
    path('diagnosis/', include('diagnosis.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
]