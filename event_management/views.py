from django.shortcuts import render
from .models import Events
from django.contrib.auth.decorators import login_required

"""Event List - Display all events in event_list.html"""
@login_required(login_url="/auth/login")
def event_list(request):
    events = Events.objects.all()  
    return render(request, 'events_management/event_list.html', {'events': events})
