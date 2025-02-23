from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

CustomUser = get_user_model() # get the currently active user model, which is CustomUser in this case, based on Django default

class CustomUserCreationForm(UserCreationForm):
    """Class to create a form for user registration"""
    class Meta:
        model = CustomUser
        fields = ("username", "password1", "password2")
