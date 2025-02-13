from django.contrib import admin
from .models import UsersInfo
from .models import FriendRequest

admin.site.register(UsersInfo)
admin.site.register(FriendRequest)