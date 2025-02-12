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
    context = {
        "plants" : {"bla" : "soup.jpg", "aaa" : "soup.jpg", "bbb" : "soup.jpg", "ccc" : "soup.jpg",
                    "ddd" : "soup.jpg", "eee" : "soup.jpg", "fff" : "soup.jpg", "ggg" : "soup.jpg",
                    "hhh" : "soup.jpg", "iii" : "soup.jpg", "jjj" : "soup.jpg", "kkk" : "soup.jpg",
                    "lll" : "soup.jpg", "mmm" : "soup.jpg", "nnn" : "soup.jpg", "ooo" : "soup.jpg"}
    }
    return render(request, "market.html", context)