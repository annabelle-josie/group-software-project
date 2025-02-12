from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

def home(request):
    return render(request, "home.html")

def leaderboard(request):
    return render(request, "leaderboard.html")

def garden(request):
    return render(request, "garden.html")

def events(request):
    return render(request, "events.html")

def market(request):
    return render(request, "market.html")