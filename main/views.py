from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
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
    return render(request, "home.html")

def leaderboard(request):
    return render(request, "leaderboard.html")

def garden(request):
    return render(request, "garden.html")

def events(request):
    return render(request, "events.html")

def market(request):
    context = {
        "plants" : {"plant1" : "soup.jpg", "plant2" : "other-soup.jpeg", "plant3" : "soup.jpg", "ccc" : "soup.jpg",
                    "ddd" : "soup.jpg", "eee" : "soup.jpg", "fff" : "soup.jpg", "ggg" : "soup.jpg",
                    "hhh" : "soup.jpg", "iii" : "soup.jpg", "jjj" : "soup.jpg", "kkk" : "soup.jpg",
                    "lll" : "soup.jpg", "mmm" : "soup.jpg", "nnn" : "soup.jpg", "ooo" : "soup.jpg"}
    }
    return render(request, "market.html", context)
  
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
            img.save("main/qrcodes/"+text+".png")
    else:
        form = QRCodeForm()
    
    return render(request, 'qr.html', {'form': form, 'qr_image_base64': qr_image_base64})