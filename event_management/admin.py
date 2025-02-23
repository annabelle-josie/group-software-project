from django.contrib import admin
from .models import Events, EventParticipants

# Register the Events model with the admin site
admin.site.register(Events)

# Register the EventParticipants model with the admin site
admin.site.register(EventParticipants)