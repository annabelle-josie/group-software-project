from django.contrib import admin
from .models import Challenge, ChallengeParticipants

class ChallengeAdmin(admin.ModelAdmin):
    readonly_fields = ("qrvalue", "QRImage")
    list_display = ["challengeId", "title", "qrvalue", "QRImage"]

admin.site.register(Challenge, ChallengeAdmin)

admin.site.register(ChallengeParticipants)
