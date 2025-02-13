from django.http import HttpResponseRedirect
from django.shortcuts import render
# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views.generic import CreateView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib import messages
from .models import *
from .serializers import *

@api_view(['POST'])
def add_challenge(request):
    serializer = ChallengeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def remove_challenge(request):
    try:
        challenge = Challenge.objects.get(pk=request.data.get('challengeId'))
        challenge.delete()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)



def home(request):
    challenges = Challenge.objects.all()
    context = {"challenge_list": challenges}
    return render(request, "home.html",context)

def leaderboard(request):
    return render(request, "leaderboard.html")

def challenges(request):
    challenges = Challenge.objects.all()
    context = {"challenge_list": challenges}
    return render(request, "allchallenges.html",context)

def garden(request):
    return render(request, "garden.html")

def events(request):
    return render(request, "events.html")

def market(request):
    return render(request, "market.html")