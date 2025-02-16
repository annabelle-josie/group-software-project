from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
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
import qrcode
from io import BytesIO
import base64
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import QRCodeForm
from event_management.models import Events, EventParticipants
from garden.models import UserGarden
from user_management.models import CustomUser, UserStats

def home(request):
    if not request.user.is_authenticated:
        return render(request, "home.html", {"plant_slots": None})  # Prevents error for anonymous users

    try:
        user_garden = UserGarden.objects.get(user=request.user)
        plant_slots = [getattr(user_garden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except UserGarden.DoesNotExist:
        plant_slots = []
    user_challenge = ChallengeParticipants.objects.filter(username=request.user,status="incomplete")

    challenge_in_progress = [
        {
            "title": challenge_participant.challengeId.title,
            "desc": challenge_participant.challengeId.desc,
            "rewardValue": challenge_participant.challengeId.rewardValue,
            "progress": challenge_participant.progress,
            "noOfTasks":challenge_participant.challengeId.noOfTasks,
            "status": challenge_participant.status,
            "id": challenge_participant.challengeId.challengeId,
        }
        for challenge_participant in user_challenge
    ]
    return render(request, "home.html", {"plant_slots": plant_slots, "challenge_list":challenge_in_progress})

def leaderboard(request):
    return render(request, "leaderboard.html")


def garden(request):
    return render(request, "garden.html")



def events(request):
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

    if request.method == "POST" and is_gamekeeper:
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        startDate = request.POST["startDate"]
        endDate = request.POST["endDate"]

        new_event = Events.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            startDate=startDate,
            endDate=endDate,
            eventMaster=request.user
        )

        all_users = User.objects.all()
        for user in all_users:
            EventParticipants.objects.create(
                username=user,
                eventId=new_event,
                progress=0, 
                status="incomplete"  
            )

        return HttpResponseRedirect(request.path)
    
    return render(request, 'events.html', {
        'events': events_with_progress,
        'is_gamekeeper': is_gamekeeper
    })
  
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

def add_challenge(request):
    if request.method == "POST":
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]

        new_challenge = Challenge.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
        )
        all_users = CustomUser.objects.all()
        for user in all_users:
            ChallengeParticipants.objects.create(
                username=user,
                challengeId=new_challenge,
                progress=0, 
                status="incomplete"  
            )

    return HttpResponseRedirect(redirect_to="/allchallenges")
    

@api_view(['DELETE'])
def remove_challenge(request):
    point = request.data.get('points')
    print("the point" + point)
    print(request.user)
    try:
        user_challenge = ChallengeParticipants.objects.get(username=request.user, challengeId= request.data.get('challengeId'))
        users = UserStats.objects.get(user=request.user)
        points = int(point) + users.points
        leaves = int(point) + users.leaves
        mystatus = user_challenge.status
        print(mystatus)
        newpoint =setattr(users,f'points',points)
        newleaves =setattr(users,f'leaves',points)
        newchallenge =setattr(user_challenge,f'status',"complete")
        users.save()
        user_challenge.save()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def remove_task(request):
    print("hi")
    challengeIds =request.data.get('challengeId')
    print(challengeIds)
    print(request.user)
    try:
        challenge = Challenge.objects.get(pk=request.data.get('challengeId'))
        print(challenge)
        user_challenge = ChallengeParticipants.objects.get(username=request.user, challengeId= request.data.get('challengeId'))
        user = user_challenge.progress +1 
        print(user)
        newprogrress =setattr(user_challenge,f'progress',user)
        user_challenge.save()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    


def mychallenges(request):
    user_challenge = ChallengeParticipants.objects.filter(username=request.user,status="incomplete")

    challenge_in_progress = [
        {
            "title": challenge_participant.challengeId.title,
            "desc": challenge_participant.challengeId.desc,
            "rewardValue": challenge_participant.challengeId.rewardValue,
            "progress": challenge_participant.progress,
            "noOfTasks":challenge_participant.challengeId.noOfTasks,
            "status": challenge_participant.status,
            "id": challenge_participant.challengeId.challengeId,
        }
        for challenge_participant in user_challenge
    ]
    
    return render(request, 'allchallenges.html', {
        'form':challengeForm(),
        'challenge_list': challenge_in_progress})