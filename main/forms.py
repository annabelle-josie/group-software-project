from django import forms
from . import models
from django.forms import ModelForm

# Form for encoding text into a QR code
class QRCodeForm(forms.Form):
    # Text field for the text to be encoded
    text = forms.CharField(label='Text to Encode', max_length=255)