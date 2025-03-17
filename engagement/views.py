import json
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from plants.models import Plant, UserGarden
from .models import UserStats, Achievement, AchievementParticipants

custom_user = get_user_model()

@login_required(login_url="/auth/login")
def leaderboard(request):
    global_data = json.loads(get_leaderboard(request).content)
    friends_data = json.loads(get_friends_leaderboard(request).content)
    
    context = {
        'leaderboard': global_data.get('leaderboard', []),
        'friend_leaderboard': friends_data.get('friend_leaderboard', []),
        'rank': global_data.get('global_rank', 0),
        'user_friend_rank': friends_data.get('user_friend_rank', 0),
    }
    return render(request, "engagement/leaderboard.html", context)

@api_view(['GET'])
def get_leaderboard(request):
    user = request.user
    global_leaders = UserStats.objects.raw(
        "SELECT id, user_id, points FROM engagement_userstats ORDER BY points DESC LIMIT 10"
    )
    data = {'leaderboard': []}
    for leader in global_leaders:
        uid = leader.user_id
        username = custom_user.objects.get(pk=uid).get_username()
        points = leader.points
        data['leaderboard'].append({'username': username, 'points': points})

    for entry in data['leaderboard']:
        try:
            user_obj = custom_user.objects.get(username=entry['username'])
            user_garden = UserGarden.objects.get(user_id=user_obj.id)
            for slot in range(1, 7):
                try:
                    plant = Plant.objects.get(id=getattr(user_garden, f"plant{slot}Id_id"))
                    entry[f'plant{slot}'] = plant.image.url
                except Plant.DoesNotExist:
                    entry[f'plant{slot}'] = '/static/potted_plant.png'
        except (custom_user.DoesNotExist, UserGarden.DoesNotExist):
            for slot in range(1, 7):
                entry[f'plant{slot}'] = '/static/potted_plant.png'

    user_rank_queryset = UserStats.objects.raw(
        "SELECT userrank, id FROM (SELECT engagement_userstats.*, RANK() OVER (ORDER BY points DESC) AS userrank FROM engagement_userstats) AS ranking WHERE user_id = %s",
        [user.id]
    )
    global_rank = None
    for item in user_rank_queryset:
        global_rank = item.userrank
    data['global_rank'] = global_rank if global_rank is not None else 0
    return JsonResponse(data)

@api_view(['GET'])
def get_friends_leaderboard(request):
    user = request.user
    friend_ids = list(user.get_friends().values_list('id', flat=True))
    friend_ids.append(user.id)
    friend_stats = UserStats.objects.filter(user_id__in=friend_ids).order_by('-points')
    data = {'friend_leaderboard': []}
    user_friend_rank = None
    for position, friend_stat in enumerate(friend_stats, start=1):
        username = friend_stat.user.get_username()
        points = friend_stat.points
        data['friend_leaderboard'].append({
            'username': username,
            'points': points,
            'friend_rank': position,
        })
        if friend_stat.user == user:
            user_friend_rank = position
    data['user_friend_rank'] = user_friend_rank if user_friend_rank is not None else 0

    for entry in data['friend_leaderboard']:
        try:
            user_obj = custom_user.objects.get(username=entry['username'])
            user_garden = UserGarden.objects.get(user_id=user_obj.id)
            for slot in range(1, 7):
                try:
                    plant = Plant.objects.get(id=getattr(user_garden, f"plant{slot}Id_id"))
                    entry[f'plant{slot}'] = plant.image.url
                except Plant.DoesNotExist:
                    entry[f'plant{slot}'] = '/static/potted_plant.png'
        except (custom_user.DoesNotExist, UserGarden.DoesNotExist):
            for slot in range(1, 7):
                entry[f'plant{slot}'] = '/static/potted_plant.png'
    return JsonResponse(data)

@login_required(login_url="/auth/login")
def achievement(request):
    user_achievements = AchievementParticipants.objects.filter(username=request.user)

    achievements = [
        {
            "id": achievement_participant.achievementId.achievementId,
            "name": achievement_participant.achievementId.name,
            "desc": achievement_participant.achievementId.desc,
            "amount": achievement_participant.achievementId.amount,
            "rewardValue": achievement_participant.achievementId.rewardValue,
            "type": achievement_participant.achievementId.type,
            "url": achievement_participant.achievementId.url,
            "progress": achievement_participant.progress,
            "status": achievement_participant.status,
            "percent": achievement_participant.progress * 100 // achievement_participant.achievementId.amount,
        }
        for achievement_participant in user_achievements
    ]
    return render(request, 'engagement/achievements.html', {'achievement_list': achievements})

@login_required
def achievementProgress(request, type, amount):
    """Handle the progress increment request."""

    if type == "onVisitSite":
        return HttpResponse("Can not progress achievements of type onVisitSite.", status=400)
    
    try:
        achievements = Achievement.objects.filter(type=type)
    except:
        return HttpResponse("Invalid request", status=400)

    for achievement in achievements:
        try:
            achievementParticipant = AchievementParticipants.objects.get(username=request.user, achievementId=achievement.achievementId)

            achievementParticipant.progress += amount
            achievementParticipant.save()

            if achievementParticipant.progress >= achievement.amount and achievementParticipant.status == "incomplete":
                user_stats = UserStats.objects.get(user=request.user)
                user_stats.leaves += achievement.rewardValue
                user_stats.points += achievement.rewardValue
                user_stats.save()
                achievementParticipant.status = "complete"
                achievementParticipant.save()
                achievementProgress(request, "onPointGain", achievement.rewardValue)
            
        except:
            return HttpResponse("Something went wrong progressing this achievement.", status=400)
        
@login_required
def achievementVisitURL(request, achievement_id):
    try:
        achievementParticipant = AchievementParticipants.objects.get(username=request.user, achievementId=achievement_id)
        achievement = achievementParticipant.achievementId
    except AchievementParticipants.DoesNotExist:
        return JsonResponse({'error': 'Achievement participant not found.'}, status=404)
    
    if achievement.type != "onVisitSite":
        return HttpResponse("Can only complete achievements of type onVisitSite.", status=400)
    
    achievementParticipant.progress = 1
    achievementParticipant.save()

    if achievementParticipant.status == "incomplete":
        user_stats = UserStats.objects.get(user=request.user)
        user_stats.leaves += achievement.rewardValue
        user_stats.points += achievement.rewardValue
        user_stats.save()
        achievementParticipant.status = "complete"
        achievementParticipant.save()
        achievementProgress(request, "onPointGain", achievement.rewardValue)

    return JsonResponse({'status': 'success'})