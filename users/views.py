from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
import os

custom_user = get_user_model()
# Explicitly set correct template path, as we arent using registration, so without this it assumes the path as /registration/login.html 
class CustomLoginView(LoginView):
    template_name = "users/login.html"

# SignUp View
class SignUpView(CreateView):
    model = custom_user
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "users/signup.html"

# Privacy View
class PrivacyView(TemplateView):
    template_name = 'users/privacy.html'

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/password_reset.html'

    def form_valid(self, form):
        print("PASSWORD: ", os.getenv("EMAIL_HOST_PASSWORD"))
        return super().form_valid(form)

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'