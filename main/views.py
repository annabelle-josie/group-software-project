from random import randint
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from challenges.models import Challenge, ChallengeParticipants
from plants.models import UserGarden

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

    currentdate = timezone.now().date()
    
    # Remove any challenge assignments that are not for today.
    ChallengeParticipants.objects.filter(username=request.user).delete()

    challenges = Challenge.objects.all()
    amount = challenges.count()

    # Assign 3 new challenges for today.
    if amount > 0:
        count = 0
        mylist = []
        while count < 3:
            # Pick a random challenge.
            challenge = challenges.order_by('?').first()
            if challenge.challengeId not in mylist:
                mylist.append(challenge.challengeId)
                ChallengeParticipants.objects.create(
                    username=request.user,
                    challengeId=challenge,
                    progress=0,
                    status="incomplete",
                    date=currentdate
                )
                count += 1

    # Retrieve the fresh list of today's challenge assignments.
    user_challenge = ChallengeParticipants.objects.filter(
        username=request.user, status="incomplete", date=currentdate
    )
    challenge_in_progress = [
        {
            "title": cp.challengeId.title,
            "desc": cp.challengeId.desc,
            "rewardValue": cp.challengeId.rewardValue,
            "progress": cp.progress,
            "noOfTasks": cp.challengeId.noOfTasks,
            "qrvalue": cp.challengeId.qrvalue,
            "id": cp.challengeId.challengeId,
            "date": cp.date,
            "isQR": cp.challengeId.isQR,  
            "QRImage": cp.challengeId.QRImage,
        }
        for cp in user_challenge
    ]

    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()

    users = custom_user.objects.get(username=request.user)
    available = users.owned_plants.all()
    return render(request, "home.html", {"plant_slots": plant_slots, "challenge_list":challenge_in_progress, "available":available, "isGamekeeper": isGamekeeper})

