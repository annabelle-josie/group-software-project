import secrets
import string
import json
import qrcode
from io import BytesIO
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from engagement.models import UserStats
from garden.models import Plant
from engagement.views import achievementProgress
from .models import Events, EventParticipants


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
            "plantReward": eventParticipant.eventId.plantReward,
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
            "plantReward": event.plantReward,
        }
        for event in availableEvents
    ]

    # Check if the user is a Game Keeper (admin role)
    isGamekeeper = request.user.groups.filter(name="Game Keepers").exists()

    if request.method == "POST" and isGamekeeper:
        title = request.POST["title"]
        desc = request.POST["desc"]
        noOfTasks = int(request.POST["noOfTasks"])
        rewardValue = int(request.POST["rewardValue"])
        startDate = request.POST["startDate"]
        endDate = request.POST["endDate"]
        isQR = request.POST["qrCode"] == "qr"
        eventImage = request.FILES.get('eventImage')
        plant_id = request.POST.get("plantReward")

        plantReward = Plant.objects.get(id=plant_id) if plant_id else None

        qr_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80)) if isQR else None

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
            eventImage=eventImage,
            plantReward=plantReward
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

    plants = Plant.objects.all()

    return render(request, 'events/events.html', {
        'events': eventsWithProgress,
        'available_events': available_events,
        'isGamekeeper': isGamekeeper,
        'plants': plants
    })


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


@login_required(login_url="/auth/login")
def scan_qr(request, event_id, qr_code):
    """Handles QR scanning, auto-registers user if not registered, and increments progress if valid."""
    try:
        event = Events.objects.get(eventId=event_id)
    except Events.DoesNotExist:
        return JsonResponse({'error': 'Invalid event.'}, status=404)

    try:
        eventParticipant = EventParticipants.objects.get(username=request.user, eventId=event)
    except EventParticipants.DoesNotExist:
        eventParticipant = EventParticipants(username=request.user, eventId=event, progress=0, status="in_progress")
        eventParticipant.save()

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
                achievementProgress(request, "onPointGain", event.rewardValue)
                achievementProgress(request, "onEventComplete", 1)
                user_stats.save()
                return redirect('events')  

        return JsonResponse({
            'progress': eventParticipant.progress,
            'totalTasks': event.noOfTasks,
            'status': eventParticipant.status,
            'completed': False
        })

    return JsonResponse({'error': 'Invalid QR code.'}, status=400)


def events_view(request):
    if request.user.is_authenticated:
        user_events = EventParticipants.objects.filter(username=request.user).values_list('eventId', flat=True)
        registered_events = Events.objects.filter(eventId__in=user_events)
        available_events = Events.objects.exclude(eventId__in=user_events)

        return render(request, 'events/events.html', {
            'events': registered_events,
            'available_events': available_events
        })
    else:
        return render(request, 'events/events.html', {
            'events': [],
            'available_events': []
        })


# increment progress view, increments the progress of an event participant and returns a JSON response for if user is not valid or success
@login_required
def incrementProgress(request, event_id):
    """Handle the progress increment request."""
    try:
        eventParticipant = EventParticipants.objects.get(username=request.user, eventId=event_id)
        event = eventParticipant.eventId
    except EventParticipants.DoesNotExist:
        return JsonResponse({'error': 'Event participant not found.'}, status=404)

    # Only try to parse JSON if the body is not empty.
    if request.body:
        try:
            data = json.loads(request.body)
            qr_code = data.get('qrCode')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    else:
        qr_code = None

    # If the event uses QR and the QR code is missing or incorrect.
    if event.isQR and (not qr_code or qr_code != event.eventQR):
        user_stats = UserStats.objects.get(user=request.user)
        return JsonResponse({
            'progress': eventParticipant.progress,
            'totalTasks': event.noOfTasks,
            'status': eventParticipant.status,
            'rewardAdded': event.rewardValue,
            'newBalance': user_stats.leaves,
            'completed': True
        }, status=400)

    if eventParticipant.progress < event.noOfTasks:
        eventParticipant.progress += 1  
        if eventParticipant.progress >= event.noOfTasks:  
            eventParticipant.status = "complete"
        eventParticipant.save()

    if eventParticipant.status == "complete":
        user_stats = UserStats.objects.get(user=request.user)
        user_stats.leaves += event.rewardValue
        user_stats.points += event.rewardValue
        # Assuming achievementProgress is defined and works as expected:
        achievementProgress(request, "onPointGain", event.rewardValue)
        achievementProgress(request, "onEventComplete", 1)
        user_stats.save()

        if event.plantReward:
            user = request.user
            plant = event.plantReward
            if plant not in user.owned_plants.all():
                # Add the plant to the user's owned plants
                user.owned_plants.add(plant)

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