from django.contrib import admin

from .models import Events, EventMembers

admin.site.register(Events)
admin.site.register(EventMembers)