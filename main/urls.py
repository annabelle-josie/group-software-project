from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Keep home in main
    path("auth/", include("login.urls")),  # Move login/signup to login app
]