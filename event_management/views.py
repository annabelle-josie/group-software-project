from django.shortcuts import render
from .models import Events

def event_list(request):
    events = Events.objects.all()  
    return render(request, 'events_management/event_list.html', {'events': events})
