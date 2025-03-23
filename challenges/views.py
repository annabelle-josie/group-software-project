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
from .models import Challenge, ChallengeParticipants

custom_user = get_user_model()

def my_challenges(request):
    user_challenge = ChallengeParticipants.objects.filter(username=request.user,status="incomplete")
    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()
    try:
        allchallenges= Challenge.objects.all()
    except:
        allchallenges = None
    return render(request, 'challenges/challengeQR.html', {'isGamekeeper': isGamekeeper, 'allchallenges':allchallenges})


# function to delete a challenge, returns a JSON response that indicates success or failure
@api_view(['DELETE'])
def remove_challenge(request):
    point = request.data.get('points')
    try:
        user_challenge = ChallengeParticipants.objects.get(username=request.user, challengeId= request.data.get('challengeId'))
        users = UserStats.objects.get(user=request.user)
        points = int(point) + users.points
        leaves = int(point) + users.leaves
        mystatus = user_challenge.status
        setattr(users,f'points',points)
        setattr(users,f'leaves',leaves)
        setattr(user_challenge,f'status',"complete")
        achievementProgress(request, "onPointGain", int(point))
        achievementProgress(request, "onChallengeComplete", 1)
        users.save()
        user_challenge.save()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


# function to remove a task from a challenge, returns a JSON response that indicates success or failure
@api_view(['POST'])
def remove_task(request):
    challengeIds =request.data.get('challengeId')
    try:
        challenge = Challenge.objects.get(pk=request.data.get('challengeId'))
        user_challenge = ChallengeParticipants.objects.get(username=request.user, challengeId= request.data.get('challengeId'))
        user = user_challenge.progress +1 
        setattr(user_challenge,f'progress',user)
        user_challenge.save()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@login_required
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
        return HttpResponseRedirect()


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