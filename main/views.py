from random import randint
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from challenges.models import Challenge, ChallengeParticipants
from engagement.models import UserStats
from garden.models import Plant, UserGarden
from garden.serializers import UserGardenSerializer

# Create views here

custom_user = get_user_model()

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
            "QRImage": challenge_participant.challengeId.QRImage, 
             
        }
        for challenge_participant in user_challenge
    ]

    users = custom_user.objects.get(username= request.user)
    available = users.owned_plants.all()
    return render(request, "home.html", {"plant_slots": plant_slots, "challenge_list":challenge_in_progress, "available":available})


def garden(request):
    return render(request, "garden.html")


@login_required(login_url="/auth/login")
def gardenView(request):
    """View to display the garden on the main page"""
    userGarden = UserGarden.objects.get(user=request.user)
    users = custom_user.objects.get(username= request.user)
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
        garden = UserGarden.objects.get(user__id=user_id)
        serializer = UserGardenSerializer(garden)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserGarden.DoesNotExist:
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

        
'''Market: only availble if logged in (otherwise nowhere to purchase plant to)
Retrieves all plants available on the market, plants owned by a given user and their points
These are then returned to the front-end within context to the market.html template
'''
@login_required(login_url="/auth/login")
def market_view(request):
    # Fetching all plants, plants owned by the user, and how many leaves that user has
    plants = Plant.objects.filter(onMarket=True).order_by('price')   # Fetch from DB only plants that are allowed to be on market
    user = custom_user.objects.get(username=request.user)
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

        user = custom_user.objects.get(username=userData)
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
        owner = custom_user.objects.get(username=username)
        userGarden = UserGarden.objects.get(user_id=owner.id)
        plant_slots = [getattr(userGarden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except:
        plant_slots = None

    return render(request, "profile.html", {"owner": username, "plant_slots": plant_slots})

