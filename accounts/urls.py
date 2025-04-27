from django.urls import path
from .views import register, user_login, user_logout, home, diagnosis_home

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("home/", home, name="home"),  # <-- Add this
    path("diagnosis/", diagnosis_home, name="diagnosis_home"),  # <-- Add this
]
