from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm

CustomUser = get_user_model() # get the currently active user model, which is CustomUser in this case, based on Django default

class CustomUserCreationForm(UserCreationForm):
    """Class to create a form for user registration"""
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email'] # update to ['username', 'email'] if username is to be updated

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']