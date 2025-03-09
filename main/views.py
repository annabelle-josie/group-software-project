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
from login.forms import ProfileUpdateForm, CustomPasswordChangeForm
from django.urls import reverse
from django.conf import settings



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
    repeatable_challenges = Challenge.objects.filter(repeatable=True)
    random_item = repeatable_challenges.count()
    if current_challenges and current_challenges.date != current:
        for i in my_user_challenge:
            if i.challengeId.repeatable is True:
                print(i.challengeId)
                # i.delete()
                my_user_challenge.get(challengeId=i.challengeId).delete()
        
        if random_item > 0:
            count=0
            mylist =[]
            while count < 3:
                random_challenge = repeatable_challenges[randint(0, random_item - 1)]
                if(random_challenge.challengeId not in mylist):
                    print(random_challenge.repeatable, random_challenge.title)
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
            "repeatable": challenge_participant.challengeId.repeatable,
        }
        for challenge_participant in user_challenge
    ]

    users = CustomUser.objects.get(username= request.user)
    available = users.owned_plants.all()
    return render(request, "home.html", {"plant_slots": plant_slots, "challenge_list":challenge_in_progress, "available":available})

@login_required(login_url="/auth/login")
def gardenView(request):
    """View to display the garden on the main page"""
    userGarden = UserGarden.objects.get(user=request.user)
    users = CustomUser.objects.get(username= request.user)
    # available = users.owned_plants.all().values()
    available = users.owned_plants.all()
    allplants= Plant.objects.filter(onMarket=True)

    plantSlots = []
    if userGarden:
        for slot in range(1, 7):  # Loop through all 6 slots
            plant = getattr(userGarden, f"plant{slot}Id", None)  # Get Plant object directly
            # print(f"Plant Slot {slot}: {plant}")  # Debugging line
            # print(f"Plant Slot {slot}: {plant}")  # Debugging line
            plantSlots.append(plant)
    # print("Final Plant Slots:", plantSlots)  # Debugging line
    return render(request, "garden/garden.html", {"plantSlots": plantSlots,"available":available, "allplants": allplants})

@api_view(["GET"])
def get_garden(request, user_id):
    """API used to display garden on the main page"""
    try:
        garden = userGarden.objects.get(user__id=user_id)
        serializer = GardenSerializer(garden)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except userGarden.DoesNotExist:
        return Response({"error": "Garden not found"}, status=status.HTTP_404_NOT_FOUND)
    
def updateGarden(request):
    """View to updte the user's garden with a new plant"""
    # print("hello")
    plantname = request.POST.get('plantname')
    slot = request.POST.get('slot')
    print(slot)
    if not plantname:
        return redirect("/")
    try:
        plant= Plant.objects.get(name=plantname)
        # print(plant)
        plantslots = UserGarden.objects.get(user=request.user)
        plantslot = setattr(plantslots, f"plant{slot}Id",plant)
        plantslots.save()
        # get right plant list and plant ID 
    except Plant.DoesNotExist:
        return Response({"error": "no "}, status=status.HTTP_404_NOT_FOUND)
    return HttpResponseRedirect(redirect_to="/")

# leaderboard view, displays the top 10 users with the most points
@login_required(login_url="/auth/login")
def leaderboard(request):
    user = request.user
    context = get_leaderboard(request).content
    context = json.loads(context)
    userrank = UserStats.objects.raw("SELECT userrank, id FROM (SELECT user_management_userstats.*, RANK() OVER (ORDER BY points DESC) as userrank FROM user_management_userstats) user_management_userstats WHERE user_id = " + str(user.id))
    for person in userrank:
        rank = person.userrank
    context['rank'] = rank
    return render(request, "leaderboard.html", context)




@login_required
def scan_qr(request, event_id, qr_code):
    """Handles QR scanning and increments progress if valid."""
    try:
        event = Events.objects.get(eventId=event_id)
        eventParticipant = EventParticipants.objects.get(username=request.user, eventId=event)
    except (Events.DoesNotExist, EventParticipants.DoesNotExist):
        return JsonResponse({'error': 'Invalid event or not registered.'}, status=404)

    if event.isQR and event.eventQR == qr_code:
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

    return JsonResponse({'error': 'Invalid QR code.'}, status=400)



def sign_up_for_event(request, event_id):
    if request.method == 'POST':
        event = Events.objects.get(eventId=event_id)
        user = request.user

        if EventParticipants.objects.filter(eventId=event, username=user).exists():
            return JsonResponse({'success': False, 'message': 'You are already signed up for this event.'})

        EventParticipants.objects.create(
            eventId=event,
            username=user,
            status='In Progress',
            progress=0
        )
        
        return JsonResponse({'success': True, 'message': 'Successfully registered for the event.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



def events_view(request):
    if request.user.is_authenticated:
        user_events = EventParticipants.objects.filter(username=request.user).values_list('eventId', flat=True)
        registered_events = Events.objects.filter(eventId__in=user_events)
        available_events = Events.objects.exclude(eventId__in=user_events)

        return render(request, 'events.html', {
            'events': registered_events,
            'available_events': available_events
        })
    else:
        return render(request, 'events.html', {
            'events': [],
            'available_events': []
        })



@login_required(login_url="/auth/login")
def events(request):
    # Fetch events where the user is a participant
    userEvents = EventParticipants.objects.filter(username=request.user)
    
    # List of events the user is signed up for, with their progress
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
            "eventImage": eventParticipant.eventId.eventImage.url if eventParticipant.eventId.eventImage else None,
            "eventMaster": eventParticipant.eventId.eventMaster.username,
        }
        for eventParticipant in userEvents
    ]
    
    # Get the IDs of the events the user is already participating in
    userEventIds = userEvents.values_list('eventId', flat=True)
    
    # Fetch all events the user is not participating in
    availableEvents = Events.objects.exclude(eventId__in=userEventIds)
    
    # List of events the user is not signed up for
    available_events = [
        {
            "eventId": event.eventId,
            "title": event.title,
            "desc": event.desc,
            "startDate": event.startDate,
            "endDate": event.endDate,
            "rewardValue": event.rewardValue,
            "eventQR": event.eventQR,
            "eventQRImage": event.eventQRImage.url if event.eventQRImage else None,
            "isQR": event.isQR,
            "eventImage": event.eventImage.url if event.eventImage else None,
            "eventMaster": event.eventMaster.username,
        }
        for event in availableEvents
    ]

    # Check if the user is a Game Keeper (admin role)
    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()

    if request.method == "POST" and isGamekeeper:
        # Handle the creation of a new event by a Game Keeper
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        startDate = request.POST["startDate"]
        endDate = request.POST["endDate"]
        isQR = request.POST["qrCode"] == "qr"
        eventImage = request.FILES.get('eventImage')

        # Generate a random QR code if selected
        qr_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80)) if isQR else None

        # Create the new event without assigning it to users yet
        newEvent = Events.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            startDate=startDate,
            endDate=endDate,
            eventMaster=request.user,
            eventQR=qr_secret,
            isQR=isQR,
            eventImage=eventImage
        )

        if isQR:
            base_url = 'down2earth.eu.pythonanywhere.com'
            qr_url = f"{base_url}{reverse('scan_qr', args=[newEvent.eventId, qr_secret])}"
            qr = qrcode.make(qr_url)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            newEvent.eventQRImage.save(f"qr_{newEvent.eventId}.png", ContentFile(buffer.getvalue()), save=False)
            newEvent.save()

        return HttpResponseRedirect(request.path)

    return render(request, 'events.html', {
        'events': eventsWithProgress,
        'available_events': available_events,
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
            "repeatable": challenge_participant.challengeId.repeatable,
        }
        for challenge_participant in user_challenge
    ]
    if request.method == "POST" and isGamekeeper:
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        isQR = request.POST["qrCode"] == "qr"  
        repeatable = request.POST["repeatable"] == "repeatable"

        qrvalue = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80)) if isQR else None

        new_challenge = Challenge.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            qrvalue= qrvalue,
            isQR =isQR,
            repeatable = repeatable,
        )
        if isQR:
            new_challenge.generateQrImage()
            new_challenge.save()
        if repeatable is False:
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

@login_required
def profile(request, username):
    try:
        owner = CustomUser.objects.get(username=username)
        userGarden = UserGarden.objects.get(user_id=owner.id)
        plant_slots = [getattr(userGarden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except:
        plant_slots = None

    return render(request, "profile.html", {"owner": username, "plant_slots": plant_slots})

@login_required()
def settings(request):
    user_form = ProfileUpdateForm(instance=request.user)
    password_form = CustomPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = ProfileUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('settings')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Your password has been changed successfully!')
                return redirect('/auth/login/')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, "settings.html", context)