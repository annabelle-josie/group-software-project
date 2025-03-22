import json
import secrets
import string
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status
from engagement.models import UserStats
from engagement.views import achievementProgress
from .forms import ChallengeForm
from .models import Challenge, ChallengeParticipants

custom_user = get_user_model()

@login_required(login_url="/auth/login")
def my_challenges(request):
    if not request.user.groups.filter(name="Game Keepers").exists():
        return HttpResponseRedirect("/")
    user_challenge = ChallengeParticipants.objects.filter(username=request.user,status="incomplete")
    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()
    try:
        allchallenges= Challenge.objects.all()
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
            "QRImage": challenge_participant.challengeId.QRImage,  
        }
        for challenge_participant in user_challenge
    ]
    if request.method == "POST" and isGamekeeper:
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = request.POST["noOfTasks"]
        rewardValue = request.POST["rewardValue"]
        isQR = request.POST["qrCode"] == "qr"

        qrvalue = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80)) if isQR else None

        new_challenge = Challenge.objects.create(
            title=title,
            desc=desc,
            noOfTasks=noOfTasks,
            rewardValue=rewardValue,
            qrvalue= qrvalue,
            isQR =isQR,
        )
        if isQR:
            new_challenge.generateQrImage()
            new_challenge.save()
        return HttpResponseRedirect(request.path)
    

    return render(request, 'challenges/allchallenges.html', {
        'form':ChallengeForm(),
        'challenge_list': challenge_in_progress, 'isGamekeeper': isGamekeeper, 'allchallenges':allchallenges})


# function to delete a challenge, returns a JSON response that indicates success or failure
@api_view(['DELETE'])
@login_required(login_url="/auth/login")
def remove_challenge(request):
    point = request.data.get('points')
    try:
        user_challenge = ChallengeParticipants.objects.get(username=request.user, challengeId=request.data.get('challengeId'))
        users = UserStats.objects.get(user=request.user)
        users.points += int(point)
        users.leaves += int(point)
        user_challenge.status = "complete"

        # Trigger achievement progress
        achievementProgress(request, "onPointGain", int(point))
        achievementProgress(request, "onChallengeComplete", 1)

        users.save()
        user_challenge.save()

        return Response(status=status.HTTP_200_OK)

    except ChallengeParticipants.DoesNotExist:
        return Response(
            {"error": "Challenge participant not found."}, status=status.HTTP_404_NOT_FOUND)


# function to remove a task from a challenge, returns a JSON response that indicates success or failure
@api_view(['POST'])
@login_required(login_url="/auth/login")
def remove_task(request):
    challenge_id = request.data.get('challengeId')
    try:
        # Ensure the challenge exists
        challenge = Challenge.objects.get(pk=challenge_id)
        user_challenge = ChallengeParticipants.objects.get(username=request.user, challengeId=challenge_id)
        # Increment progress
        user_challenge.progress += 1
        user_challenge.save()

        return Response(status=status.HTTP_200_OK)

    except (Challenge.DoesNotExist, ChallengeParticipants.DoesNotExist):
        return Response(status=status.HTTP_404_NOT_FOUND)




@login_required(login_url="/auth/login")
def challenge_increment_progress(request, challenge_id):
    """Handle the progress increment request."""
    try:
        challenge_participant = ChallengeParticipants.objects.get(username=request.user, challengeId=challenge_id)
        challenge = challenge_participant.challengeId
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
        return HttpResponseRedirect('/')
    
    return JsonResponse({"message": "Progress incremented."})


@login_required(login_url="/auth/login")
def scan_challenge(request, challenge_id, qr_code):
    """Handles QR scanning, auto-registers user if not registered, and increments progress if valid."""
    try:
        challenge = Challenge.objects.get(challengeId = challenge_id)
    except Challenge.DoesNotExist:
        return JsonResponse({'error': 'Invalid challenge.'}, status=404)
    try:
        ChallengeParticipant = ChallengeParticipants.objects.get(username=request.user, challengeId=challenge)
    except ChallengeParticipants.DoesNotExist:
        ChallengeParticipant = ChallengeParticipants(username=request.user, challengeId=challenge, progress=0, status="incomplete")
        ChallengeParticipant.save()

    if challenge.isQR and challenge.qrvalue == qr_code:
        if ChallengeParticipant.progress < challenge.noOfTasks:
            ChallengeParticipant.progress += 1
            if ChallengeParticipant.progress >= challenge.noOfTasks:
                ChallengeParticipant.status = "complete"
            
            ChallengeParticipant.save()

            if ChallengeParticipant.status == "complete":
                user_stats = UserStats.objects.get(user=request.user)
                user_stats.leaves += challenge.rewardValue
                user_stats.points += challenge.rewardValue
                user_stats.save()
                return HttpResponseRedirect("home")

        return JsonResponse({
            'progress': ChallengeParticipant.progress,
            'totalTasks': challenge.noOfTasks,
            'status': ChallengeParticipant.status,
            'completed': False
        })

    return JsonResponse({'error': 'Invalid QR code.'}, status=400)