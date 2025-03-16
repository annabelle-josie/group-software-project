from django.contrib import admin
from .models import CustomUser, Friendship

admin.site.register(CustomUser)

admin.site.register(Friendship) 