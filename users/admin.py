from django.contrib import admin
from .models import CustomUser, UserStats, Friendship

admin.site.register(CustomUser)
admin.site.register(UserStats)
admin.site.register(Friendship) 