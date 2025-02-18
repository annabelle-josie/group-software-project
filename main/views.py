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
from django.contrib.auth import get_user_model
from garden.models import UserGarden
from user_management.models import CustomUser, UserStats
from django.shortcuts import get_object_or_404
from user_management.models import UserStats, CustomUser
from garden.models import Plant
import json

User = get_user_model()

@login_required(login_url="/auth/login")

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

@login_required(login_url="/auth/login")
def leaderboard(request):
    context = get_leaderboard(request).content
    context = json.loads(context)
    context['points'] = UserStats.objects.get(user_id=request.user.id).points
    return render(request, "leaderboard.html", context)

def challenges(request):
    challenges = Challenge.objects.all()
    try:
        users = UserStats.objects.get(user=request.user)
        stuff =users.points
    except:
        stuff=[]
    context = {"challenge_list": challenges, "users":stuff}
    return render(request, "allchallenges.html", context)

def garden(request):
    return render(request, "garden.html")


@login_required(login_url="/auth/login")
def events(request):
    user_events = EventParticipants.objects.filter(username=request.user)

    events_with_progress = [
        {
            "eventId": event_participant.eventId.eventId,
            "title": event_participant.eventId.title,
            "desc": event_participant.eventId.desc,
            "startDate": event_participant.eventId.startDate,
            "endDate": event_participant.eventId.endDate,
            "rewardValue": event_participant.eventId.rewardValue,
            "progress": event_participant.progress,
            "noOfTasks": event_participant.eventId.noOfTasks,
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


@login_required
def increment_progress(request, event_id):
    """Handle the progress increment request."""
    try:
        event_participant = EventParticipants.objects.get(username=request.user, eventId=event_id)
    except EventParticipants.DoesNotExist:
        return JsonResponse({'error': 'Event participant not found.'}, status=404)

    if event_participant.progress < event_participant.eventId.noOfTasks:
        event_participant.increment_progress()

        
        if event_participant.progress >= event_participant.eventId.noOfTasks:
            event_participant.status = "complete"
            event_participant.save()

      
            user_stats = UserStats.objects.get(user=request.user)
            user_stats.leaves += event_participant.eventId.rewardValue
            user_stats.points += event_participant.eventId.rewardValue
            user_stats.save()

            return JsonResponse({
                'progress': event_participant.progress,
                'totalTasks': event_participant.eventId.noOfTasks,
                'status': event_participant.status,
                'rewardAdded': event_participant.eventId.rewardValue,
                'newBalance': user_stats.leaves
            })

    return JsonResponse({
        'progress': event_participant.progress,
        'totalTasks': event_participant.eventId.noOfTasks,
        'status': event_participant.status
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

@api_view(['GET'])
def get_leaderboard(request):
    leaders = UserStats.objects.raw("SELECT id, user_id, points FROM user_management_userstats ORDER BY points DESC LIMIT 10")
    data = {'leaderboard': []}
    for person in leaders:
        id = person.user_id
        username = CustomUser.objects.get(pk=id).get_username()
        points = person.points
        data['leaderboard'].append({'username': username, 'points': points})
    return JsonResponse(data)
    

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
=======
@login_required(login_url="/auth/login")
def market_view(request):
    plants = Plant.objects.filter(onMarket=True)   # Fetch all plants from DB that are allowed to be on market
    
    user = CustomUser.objects.get(username=request.user)
    current_leaves = UserStats.objects.get(user_id=user.id).leaves

    # current_leaves = 80  # Need to replace with a method to get that users leaves
    
    context = {
        "plants": plants,
        "leaves": current_leaves
    }
    return render(request, "market.html", context)

@api_view(['POST'])
def add_purchased_plant(request):
    # try:
        plantName = request.data.get('plantName')
        userData = request.data.get('user')

        user = CustomUser.objects.get(username=userData)
        currentPlants = user.owned_plants.all()
        plant = Plant.objects.get(name=plantName)
        userStatObj = UserStats.objects.get(user_id=user.id)
        userLeaves = userStatObj.leaves

        if(plant.price <= userLeaves):
            ownList = []
            for i in range(len(currentPlants)):
                ownList.append(currentPlants[i])
            ownList.append(plant)

            user.owned_plants.set(ownList)

            newLeaves = userLeaves - plant.price
            userStatObj.leaves = newLeaves
            userStatObj.save()
            return Response(status=status.HTTP_200_OK)
        else:
            print("YOU ARE BROKE (But not broken?)")
            return Response(status=status.HTTP_400_BAD_REQUEST)
    # except:
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
