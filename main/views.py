from random import randint
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
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
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
        userGarden = UserGarden.objects.get(user=request.user)
        plant_slots = [getattr(userGarden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except UserGarden.DoesNotExist:
        plant_slots = []
    try:
        current_challenges = ChallengeParticipants.objects.latest('date')
    except ChallengeParticipants.DoesNotExist:
               current_challenges = None
    my_user_challenge = ChallengeParticipants.objects.filter(username=request.user)
    current = timezone.now().date()
    repeatble_challenges = Challenge.objects.filter(repeatble=True)
    random_item = repeatble_challenges.count()
    if current_challenges and current_challenges.date != current:
        for i in my_user_challenge:
            if i.challengeId.repeatble is True:
                print(i.challengeId)
                # i.delete()
                my_user_challenge.get(challengeId=i.challengeId).delete()
        count=0
        mylist =[]
        while count < 3:
            random_challenge = repeatble_challenges[randint(0, random_item - 1)]
            if(random_challenge.challengeId not in mylist):
                print(random_challenge.repeatble, random_challenge.title)
                mylist.append(random_challenge.challengeId)
                ChallengeParticipants.objects.create(
                    username=request.user,
                    challengeId=random_challenge,
                    progress=0, 
                    status="incomplete"  
                )
                count += 1
        print(mylist)
    user_challenge = ChallengeParticipants.objects.filter(username=request.user, status="incomplete")
    challenge_in_progress = [
        {
            "title": challenge_participant.challengeId.title,
            "desc": challenge_participant.challengeId.desc,
            "rewardValue": challenge_participant.challengeId.rewardValue,
            "progress": challenge_participant.progress,
            "noOfTasks":challenge_participant.challengeId.noOfTasks,
            "qrvalue":challenge_participant.challengeId.qrvalue,
            "id": challenge_participant.challengeId.challengeId,
            "date": challenge_participant.date,
            "isQR": challenge_participant.challengeId.isQR,  
            "repeatble": challenge_participant.challengeId.repeatble,
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

def garden(request):
    return render(request, "garden.html")

# events view, displays all events (incl. progress, dynamic content, etc) and returns the events page
@login_required(login_url="/auth/login")
def events(request):
    userEvents = EventParticipants.objects.filter(username=request.user)

    eventsWithProgress = [
        {
            "eventId": eventParticipant.eventId.eventId,
            "title": eventParticipant.eventId.title,
            "desc": eventParticipant.eventId.desc,
            "startDate": eventParticipant.eventId.startDate,
            "endDate": eventParticipant.eventId.endDate,
            "rewardValue": eventParticipant.eventId.rewardValue,
            "progress": eventParticipant.progress,
            "noOfTasks": eventParticipant.eventId.noOfTasks,
            "status": eventParticipant.status,
            "eventQR": eventParticipant.eventId.eventQR,
            "eventQRImage": eventParticipant.eventId.eventQRImage.url if eventParticipant.eventId.eventQRImage else None,
            "isQR": eventParticipant.eventId.isQR,  
            "eventMaster": eventParticipant.eventId.eventMaster.username,
        }
        for eventParticipant in userEvents
    ]

    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()

    if request.method == "POST" and isGamekeeper:
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        startDate = request.POST["startDate"]
        endDate = request.POST["endDate"]
        isQR = request.POST["qrCode"] == "qr"  

        eventQR = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80)) if isQR else None

        newEvent = Events.objects.create(
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
            newEvent.generateQrImage()
            newEvent.save()

        allUsers = User.objects.all()  
        for user in allUsers:
            EventParticipants.objects.create(
                username=user,
                eventId=newEvent,
                progress=0, 
                status="incomplete"  
            )

        return HttpResponseRedirect(request.path)

    return render(request, 'events.html', {
        'events': eventsWithProgress,
        'isGamekeeper': isGamekeeper
    })

# function to delete an event, returns a JSON response that indicates success or failure
def delete_event(request, event_id):
    if request.method == "DELETE":
        event = get_object_or_404(Events, eventId=event_id)
        if request.user.username == event.eventMaster.username or request.user.is_superuser:
            event.delete()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Permission denied"}, status=403)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

# increment progress view, increments the progress of an event participant and returns a JSON response for if user is not valid or success
@login_required
def incrementProgress(request, event_id):
    """Handle the progress increment request."""
    try:
        eventParticipant = EventParticipants.objects.get(username=request.user, eventId=event_id)
        event = eventParticipant.eventId
    except EventParticipants.DoesNotExist:
        return JsonResponse({'error': 'Event participant not found.'}, status=404)

    try:
        data = json.loads(request.body)
        qr_code = data.get('qrCode')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    if event.isQR and (not qr_code or qr_code != event.eventQR):
        return JsonResponse({'progress': eventParticipant.progress,
            'totalTasks': event.noOfTasks,
            'status': eventParticipant.status,
            'rewardAdded': event.rewardValue,
            'newBalance': user_stats.leaves,
            'completed': True}, status=400)

    if eventParticipant.progress < event.noOfTasks:
        eventParticipant.progress += 1  
        if eventParticipant.progress >= event.noOfTasks:  
            eventParticipant.status = "complete"
        eventParticipant.save()

    if eventParticipant.status == "complete":
        user_stats = UserStats.objects.get(user=request.user)
        user_stats.leaves += event.rewardValue
        user_stats.points += event.rewardValue
        user_stats.save()

        return JsonResponse({
            'progress': eventParticipant.progress,
            'totalTasks': event.noOfTasks,
            'status': eventParticipant.status,
            'rewardAdded': event.rewardValue,
            'newBalance': user_stats.leaves,
            'completed': True 
        })

    return JsonResponse({
        'progress': eventParticipant.progress,
        'totalTasks': event.noOfTasks,
        'status': eventParticipant.status,
        'completed': False
    })

@login_required
def challenge_increment_progress(request, challenge_id):
    """Handle the progress increment request."""
    try:
        challenge_participant = ChallengeParticipants.objects.get(username=request.user, challengeId=challenge_id)
        challenge = challenge_participant.challengeId
        print(challenge.challengeId)
    except ChallengeParticipants.DoesNotExist:
        return JsonResponse({'error': 'challenge participant not found.'}, status=404)

    if challenge_participant.progress < challenge.noOfTasks:
        challenge_participant.progress += 1  
        if challenge_participant.progress >= challenge.noOfTasks:  
            challenge_participant.status = "complete"
        challenge_participant.save()

    if challenge_participant.status == "complete":
        user_stats = UserStats.objects.get(user=request.user)
        user_stats.leaves += challenge.rewardValue
        user_stats.points += challenge.rewardValue
        user_stats.save()

    
# function to delete a challenge, returns a JSON response that indicates success or failure
@api_view(['DELETE'])
def remove_challenge(request):
    point = request.data.get('points')
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
   
# function to view user's challenges, returns a list of challenges that the user is currently participating in and add new challenges
def my_challenges(request):
    user_challenge = ChallengeParticipants.objects.filter(username=request.user,status="incomplete")
    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()
    try:
        allchallenges= Challenge.objects.latest('challengeId')
    except:
        allchallenges = None
    challenge_in_progress = [
        {
            "title": challenge_participant.challengeId.title,
            "desc": challenge_participant.challengeId.desc,
            "rewardValue": challenge_participant.challengeId.rewardValue,
            "progress": challenge_participant.progress,
            "noOfTasks":challenge_participant.challengeId.noOfTasks,
            "status": challenge_participant.status,
            "qrvalue":challenge_participant.challengeId.qrvalue,
            "id": challenge_participant.challengeId.challengeId,
            "isQR": challenge_participant.challengeId.isQR,  
            "repeatble": challenge_participant.challengeId.repeatble,
        }
        for challenge_participant in user_challenge
    ]
    if request.method == "POST" and isGamekeeper:
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        isQR = request.POST["qrCode"] == "qr"  
        repeatble = request.POST["repeatble"] == "repeatble"

        qrvalue = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80)) if isQR else None

        new_challenge = Challenge.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            qrvalue= qrvalue,
            isQR =isQR,
            repeatble = repeatble,
        )
        if isQR:
            new_challenge.generateQrImage()
            new_challenge.save()
        if repeatble is False:
            all_users = CustomUser.objects.all()
            for user in all_users:
                ChallengeParticipants.objects.create(
                    username=user,
                    challengeId=new_challenge,
                    progress=0, 
                    status="incomplete"  
            )
        return HttpResponseRedirect(request.path)
    

    return render(request, 'allchallenges.html', {
        'form':challengeForm(),
        'challenge_list': challenge_in_progress, 'isGamekeeper': isGamekeeper, 'challenges':allchallenges})
        
'''Market: only availble if logged in (otherwise nowhere to purchase plant to)
Retrieves all plants available on the market, plants owned by a given user and their points
These are then returned to the front-end within context to the market.html template
'''
@login_required(login_url="/auth/login")
def market_view(request):
    # Fetching all plants, plants owned by the user, and how many leaves that user has
    plants = Plant.objects.filter(onMarket=True)   # Fetch from DB only plants that are allowed to be on market
    user = CustomUser.objects.get(username=request.user)
    currentLeaves = UserStats.objects.get(user_id=user.id).leaves
    ownedPlants = user.owned_plants.all()
    
    context = {
        "plants": plants,
        "leaves": currentLeaves,
        "ownedPlants" : ownedPlants
    }
    return render(request, "market.html", context)


'''Used by the front-end to purchase a plant.
Plant passed in the request along with the user. This data is used to find the matching plant in the database and 
add it to the user's owned plant list provided the user can afford to buy the plant.
'''
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

        if(plant.price <= userLeaves): # If the user can afford the plant
            # Create a list of plants, and add the new one to it
            ownList = []
            for i in range(len(currentPlants)):
                ownList.append(currentPlants[i])
            ownList.append(plant)

            # Set that appended list as the new list belonging to the user
            user.owned_plants.set(ownList)

            #Adjust the users leaf count
            newLeaves = userLeaves - plant.price
            userStatObj.leaves = newLeaves
            
            # Save the user's leaf count
            userStatObj.save()

            # Send confirmation to front-end that the purchase was successful
            return Response(status=status.HTTP_200_OK)
        else: # If the user cannot afford it, send back a bad response and abort purchase
            return Response(status=status.HTTP_400_BAD_REQUEST)


def profile(request, username):
    try:
        owner = CustomUser.objects.get(username=username)
        userGarden = UserGarden.objects.get(user_id=owner.id)
        plant_slots = [getattr(userGarden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except:
        plant_slots = None

    return render(request, "profile.html", {"owner": username, "plant_slots": plant_slots})