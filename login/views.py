from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy

CustomUser = get_user_model()
# Explicitly set correct template path, as we arent using registration, so without this it assumes the path as /registration/login.html 
class CustomLoginView(LoginView):
    template_name = "login/login.html" 

# SignUp View
class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "login/signup.html"
