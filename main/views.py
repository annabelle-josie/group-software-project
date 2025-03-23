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
    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()
    if not request.user.is_authenticated:
        return render(request, "home.html", {"plant_slots": None})  # Prevents error for anonymous users
    try:
        userGarden = UserGarden.objects.get(user=request.user)
        plant_slots = [getattr(userGarden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except UserGarden.DoesNotExist:
        plant_slots = []
    try:
        user = request.user
        my_user_challenge = ChallengeParticipants.objects.filter(username=request.user)
        findchallenge = ChallengeParticipants.objects.raw(
        "SELECT id,username_id, date FROM challenges_ChallengeParticipants"
        )
        found = False
        for leader in findchallenge:
            current = leader.username_id
            if current == user.id:
                date = leader.date
                found = True
    except ChallengeParticipants.DoesNotExist:
        my_user_challenge = None
        found = False
        date = None
    challenges = Challenge.objects.all()
    currentdate = timezone.now().date()
    amount = challenges.count()
    update = False
    if (found):
        for i in my_user_challenge:
            if date != currentdate:
                my_user_challenge.get(challengeId=i.challengeId).delete()
                update = True
    
    if found is False and challenges :
        update = True
    if update is True:
        if amount > 0 :
            count=0
            mylist =[]
            while count < 3:
                challenge = challenges[randint(0, amount - 1)]
                if(challenge.challengeId not in mylist):
                    mylist.append(challenge.challengeId)
                    ChallengeParticipants.objects.create(
                        username=request.user,
                        challengeId=challenge,
                        progress=0, 
                        status="incomplete"  

                    )
                    count += 1
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
            "QRImage": challenge_participant.challengeId.QRImage, 
             
        }
        for challenge_participant in user_challenge
    ]

    users = custom_user.objects.get(username= request.user)
    available = users.owned_plants.all()
    return render(request, "home.html", {"plant_slots": plant_slots, "challenge_list":challenge_in_progress, "available":available, "isGamekeeper":isGamekeeper})

@login_required
def profile(request, username):
    try:
        owner = custom_user.objects.get(username=username)
        userGarden = UserGarden.objects.get(user_id=owner.id)
        plant_slots = [getattr(userGarden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except:
        plant_slots = None

    return render(request, "profile.html", {"owner": username, "plant_slots": plant_slots})

