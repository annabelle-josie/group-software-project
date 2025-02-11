from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("", include("django.contrib.auth.urls")),
    path("signup", views.SignUpView.as_view(), name="signup"),
]