from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, SignUpView, PrivacyView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),  # Use CustomLoginView
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
]
