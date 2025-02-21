from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib import messages
from .models import *
import secrets
import string
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

# Create views here

User = get_user_model()

# home view, displays the user's garden and challenges
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
            "qrvalue":challenge_participant.challengeId.qrvalue,
            "id": challenge_participant.challengeId.challengeId,
        }
        for challenge_participant in user_challenge
    ]
    return render(request, "home.html", {"plant_slots": plant_slots, "challenge_list":challenge_in_progress})

# leaderboard view, displays the top 10 users with the most points
@login_required(login_url="/auth/login")
def leaderboard(request):
    context = get_leaderboard(request).content
    context = json.loads(context)
    context['points'] = UserStats.objects.get(user_id=request.user.id).points
    return render(request, "leaderboard.html", context)

# challenges view, displays all challenges and returns the allchallenges page
def challenges(request):
    challenges = Challenge.objects.all()
    try:
        users = UserStats.objects.get(user=request.user)
        stuff =users.points
    except:
        stuff=[]
    context = {"challenge_list": challenges, "users":stuff}
    return render(request, "allchallenges.html", context)

# garden view, returns the garden page
def garden(request):
    return render(request, "garden.html")

# events view, displays all events (incl. progress, dynamic content, etc) and returns the events page
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
            "eventQR": event_participant.eventId.eventQR,
            "eventQRImage": event_participant.eventId.eventQRImage.url if event_participant.eventId.eventQRImage else None,
            "isQR": event_participant.eventId.isQR,  
            "eventMaster": event_participant.eventId.eventMaster.username,
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
        isQR = request.POST["qrCode"] == "qr"  

        eventQR = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80)) if isQR else None

        new_event = Events.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            startDate=startDate,
            endDate=endDate,
            eventMaster=request.user,
            eventQR=eventQR,
            isQR=isQR
        )

        if isQR:
            new_event.generate_qr_image()
            new_event.save()

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

# function to delete an event, returns a JSON response that indicates success or failure
def delete_event(request, event_id):
    if request.method == "DELETE":
        event = get_object_or_404(Events, eventId=event_id)
        if request.user.username == event.eventMaster or request.user.is_superuser:
            event.delete()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Permission denied"}, status=403)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

# increment progress view, increments the progress of an event participant and returns a JSON response for if user is not valid or success
@login_required
def increment_progress(request, event_id):
    try:
        event_participant = EventParticipants.objects.get(username=request.user, eventId=event_id)
        event = event_participant.eventId
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
        'totalTasks': event.noOfTasks,
        'status': event_participant.status,
        'completed': False
    })

# function to generate a QR code, returns a QR code image in base64 format from qr html page
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
            location = "main/qrcodes/"+text+".png"
            img.save(location)
            # to download to computer
            # response = HttpResponse(location, content_type='application/force-download')
            # response['Content-Disposition'] = f'attachment; filename="qrcode.png"'
            # return response
    else:
        form = QRCodeForm()
    
    return render(request, 'qr.html', {'form': form, 'qr_image_base64': qr_image_base64})

# function to add a challenge, returns a redirect to the allchallenges page
# def save_image(request):
#     # image = request.data.get("qrcode")
#     print("i work ")
#     #
#     return response

def add_challenge(request):
    is_gamekeeper = request.user.groups.filter(name="Game Keepers").exists()

    if request.method == "POST" and is_gamekeeper:
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        qrvalue = request.POST["qrvalue"]

        new_challenge = Challenge.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            qrvalue= qrvalue,
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
    
# function to delete a challenge, returns a JSON response that indicates success or failure
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

# function to get the leaderboard, returns a JSON response with the top 10 users with the most points
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
    
# function to remove a task from a challenge, returns a JSON response that indicates success or failure
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
   
# function to view user's challenges, returns a list of challenges that the user is currently participating in
def mychallenges(request):
    user_challenge = ChallengeParticipants.objects.filter(username=request.user,status="incomplete")
    is_gamekeeper = request.user.groups.filter(name="Game Keepers").exists()

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
        'challenge_list': challenge_in_progress, 'is_gamekeeper': is_gamekeeper})
        
@login_required(login_url="/auth/login")
def market_view(request):
    plants = Plant.objects.filter(onMarket=True)   # Fetch all plants from DB that are allowed to be on market
    
    user = CustomUser.objects.get(username=request.user)
    current_leaves = UserStats.objects.get(user_id=user.id).leaves
    
    context = {
        "plants": plants,
        "leaves": current_leaves
    }
    return render(request, "market.html", context)

# function to add a purchased plant, returns a JSON response that indicates success or failure and updates the user's owned plants and leaves
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
