from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from rest_framework.response import Response
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework import status
from .models import *
from .forms import QRCodeForm
import qrcode
from io import BytesIO
import base64

def home(request):
    return render(request,'home.html')

def generate_qr(request):
    qr_image_base64 = None
    if request.method == 'POST':
        form = QRCodeForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
            img.save("main/qrcodes/mypng.png")
    else:
        form = QRCodeForm()
    
    return render(request, 'qr.html', {'form': form, 'qr_image_base64': qr_image_base64})