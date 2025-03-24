import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Class to create a form for user registration"""
    privacy_policy = forms.BooleanField(
        required=True,
        label="I have read and agree to the Privacy Policy"
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "privacy_policy")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['privacy_policy'].widget.attrs.update({'class': 'form-check-input'})

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            if len(password) < 8:
                raise ValidationError("The password must be at least 8 characters long.")
            if not re.search(r'[a-zA-Z]', password):
                raise ValidationError("The password must contain at least one letter.")
            if not re.search(r'\d', password):
                raise ValidationError("The password must contain at least one number.")
            if not re.search(r'[^\w\s]', password):
                raise ValidationError("The password must contain at least one special character.")
        return password
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if (password1 != password2):
                raise ValidationError("The two password fields didn’t match.")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if not re.match(r'^\w+$', username):
                raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']
        widgets = {
            'email': forms.TextInput(attrs={'class':'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control'})

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
        widgets = {
            'old_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'new_password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'new_password2': forms.PasswordInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            if len(password) < 8:
                raise ValidationError("The new password must be at least 8 characters long.")
            if not re.search(r'[a-zA-Z]', password):
                raise ValidationError("The new password must contain at least one letter.")
            if not re.search(r'\d', password):
                raise ValidationError("The new password must contain at least one number.")
            if not re.search(r'[^\w\s]', password):
                raise ValidationError("The new password must contain at least one special character.")
        return password
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if (password1 != password2):
                raise ValidationError("The two password fields didn’t match.")
        return password2
