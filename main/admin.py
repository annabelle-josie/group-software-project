from django.contrib import admin
from .models import *

# Register the Challenge model with the admin site
admin.site.register(Challenge,ChallengeAdmin)

# Register the ChallengeParticipants model with the admin site
admin.site.register(ChallengeParticipants)

# Register the Achievement model with the admin site
admin.site.register(Achievement)

# Register the AchievementParticipants model with the admin site
admin.site.register(AchievementParticipants)

# Register your models here.