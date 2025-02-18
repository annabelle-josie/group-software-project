from django.shortcuts import render
from .models import Events
from django.contrib.auth.decorators import login_required

@login_required(login_url="/auth/login")
def event_list(request):
    events = Events.objects.all()  
    return render(request, 'events_management/event_list.html', {'events': events})
