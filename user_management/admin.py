from django.contrib import admin
from .models import CustomUser, UserStats, FriendRequest

admin.site.register(CustomUser)
admin.site.register(UserStats)
admin.site.register(FriendRequest)