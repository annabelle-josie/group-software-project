from django import forms
from . import models
from django.forms import ModelForm

class QRCodeForm(forms.Form):
    text = forms.CharField(label='Text to Encode', max_length=255)
