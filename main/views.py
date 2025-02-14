from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
# from django.urls import reverse_lazy
# from django.views.generic import CreateView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib import messages
from .models import *
from .serializers import *
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
from event_management.models import Events, EventParticipants

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
    """Shows events where the user is a participant"""
    user_events = EventParticipants.objects.filter(username=request.user)

    events_with_progress = [
        {
            "title": event_participant.eventId.title,
            "desc": event_participant.eventId.desc,
            "startDate": event_participant.eventId.startDate,
            "endDate": event_participant.eventId.endDate,
            "rewardValue": event_participant.eventId.rewardValue,
            "progress": event_participant.progress,
            "status": event_participant.status,
        }
        for event_participant in user_events
    ]

    is_gamekeeper = request.user.groups.filter(name="Game Keepers").exists()

    return render(request, "events.html", {"events": events_with_progress, "is_gamekeeper": is_gamekeeper})


def create_event(request):
    if not request.user.groups.filter(name="gamekeeper").exists():
        return redirect("events")  

    if request.method == "POST":
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        startDate = request.POST["startDate"]
        endDate = request.POST["endDate"]

        Events.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            startDate=startDate,
            endDate=endDate,
            eventMaster=request.user,
        )

        return redirect("events")  

    return render(request, "create_event.html") 





def market(request):
    return render(request, "market.html")
  
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