from django.contrib import admin
from .models import CustomUser, UserStats, FriendRequest

admin.site.register(CustomUser) # Register the CustomUser model
admin.site.register(UserStats) # Register the UserStats model
admin.site.register(FriendRequest) # Register the FriendRequest model