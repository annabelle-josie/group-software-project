from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

# Explicitly set correct template path, as we arent using registration, so without this it assumes the path as /registration/login.html 
class CustomLoginView(LoginView):
    template_name = "login/login.html" 

# SignUp View
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "login/signup.html"
