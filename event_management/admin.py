from django.contrib import admin

from .models import Events, EventParticipants

admin.site.register(Events)
admin.site.register(EventParticipants)