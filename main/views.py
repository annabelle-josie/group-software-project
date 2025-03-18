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

@login_required
def profile(request, username):
    try:
        owner = custom_user.objects.get(username=username)
        userGarden = UserGarden.objects.get(user_id=owner.id)
        plant_slots = [getattr(userGarden, f"plant{slot}Id", None) for slot in range(1, 7)]
    except:
        plant_slots = None

    return render(request, "profile.html", {"owner": username, "plant_slots": plant_slots})

