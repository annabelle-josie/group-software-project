from django.contrib import admin
from .models import UserStats, Achievement, AchievementParticipants

admin.site.register(UserStats)
admin.site.register(Achievement)
admin.site.register(AchievementParticipants)
