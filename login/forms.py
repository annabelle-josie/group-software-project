from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "password1", "password2")
