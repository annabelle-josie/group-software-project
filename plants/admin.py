from django.contrib import admin
from .models import Plant, UserGarden 

# Registed models for Plant and UserGarden
admin.site.register(Plant)
admin.site.register(UserGarden)

