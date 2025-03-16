from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Class to create a form for user registration"""
    privacy_policy = forms.BooleanField(required=True, label="I have read and agree to the Privacy Policy")

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "privacy_policy")
        help_texts = {
            'password1': (
                "Your password can’t be too similar to your other personal information.\n"
                "Your password must contain at least 8 characters.\n"
                "Your password can’t be a commonly used password.\n"
                "Your password can’t be entirely numeric."
            ),
            'password2': 'Enter the same password as before, for verification.',
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email'] # update to ['username', 'email'] if username is to be updated

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']