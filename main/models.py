import secrets
import string
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ModelForm
from django.contrib.auth import get_user_model
import qrcode
from django.contrib import admin
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.timezone import now
from django.utils import timezone

# Model representing a challenge
class Challenge(models.Model):
    challengeId = models.AutoField(primary_key=True)  # Primary key for the challenge
    title = models.CharField(max_length=50)  # Title of the challenge
    desc = models.CharField(max_length=500)  # Description of the challenge
    noOfTasks = models.IntegerField()  # Number of tasks in the challenge
    rewardValue = models.IntegerField()  # Reward value for completing the challenge
    qrvalue = models.CharField(max_length=50, default=None, null=True, blank=True)
    QRImage = models.ImageField(upload_to="qr_codes/", default=None, null=True, blank=True)
    isQR = models.BooleanField(default=False)
    repeatable = models.BooleanField(default=False)
    # could have repeatable achivements not reapeatble only reset daily when complete achivement get acheivement added to a list 

    def __str__(self):
        return self.title  # String representation of the challenge
# Form for creating or updating a challenge
class ChallengeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        print(obj.challengeId)
        if (obj.isQR is True):
            obj.qrvalue = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(80))
            qr = qrcode.make(obj.qrvalue)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            obj.QRImage.save(f"qr_{obj.challengeId}.png", ContentFile(buffer.getvalue()), save=False)
        return super().save_model(request, obj, form, change)
    
    readonly_fields =("qrvalue","QRImage")
    list_display=["challengeId","title","qrvalue","QRImage"]
    #,"desc", "noOfTasks","rewardValue", "isQR","repeatable"

class challengeForm(ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'desc', 'noOfTasks', 'rewardValue', 'qrvalue']  # Fields to include in the form

# Model representing participants in a challenge
class ChallengeParticipants(models.Model):
    username = models.ForeignKey("user_management.CustomUser", on_delete=models.CASCADE)  # Reference to the user
    challengeId = models.ForeignKey(Challenge, on_delete=models.CASCADE)  # Reference to the challenge
    progress = models.IntegerField(default=0)  # Progress of the user in the challenge
    date = models.DateField(default= now)

    STATUS_CHOICES = [
        ("incomplete", "Incomplete"),
        ("complete", "Complete"),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="incomplete")  # Status of the challenge

    # Meta class for the model, including verbose names and unique constraints
    class Meta:
        verbose_name = "Challenge Members"
        verbose_name_plural = "Challenge Participants"
        unique_together = ("username", "challengeId")  # Ensure unique combination of user and challenge

    def __str__(self):
        return f"{self.username.username} - {self.challengeId.title}"  # String representation of the participant

    # Signal receiver to assign new users to existing challenges
    @receiver(post_save, sender=get_user_model())
    def assignUserToExistingChallenges(sender, instance, created, **kwargs):
        if created:
            existing_challenges = Challenge.objects.all()  # Get all existing challenges
            for challenge in existing_challenges:
                if not ChallengeParticipants.objects.filter(username=instance, challengeId=challenge).exists():
                    ChallengeParticipants.objects.create(
                        username=instance,
                        challengeId=challenge,
                        progress=0,
                        status="incomplete"
                    )  # Assign the new user to each existing challenge

class Achievement(models.Model):
    achievementId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=500)
    amount = models.IntegerField()
    rewardValue = models.IntegerField()

    TYPE_CHOICES = [
        ("onPointGain", "Points Gained"),
        ("onEventComplete", "Events Completed"),
        ("onChallengeComplete", "Challenges Completed"),
        ("onVisitSite", "Visited Website")
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="onPointGain")
    url = models.CharField(max_length=200, null=True, default=None)

    def __str__(self):
        return self.name
    
class AchievementParticipants(models.Model):
    username = models.ForeignKey("user_management.CustomUser", on_delete=models.CASCADE)  # Reference to the user
    achievementId = models.ForeignKey(Achievement, on_delete=models.CASCADE)  # Reference to the challenge
    progress = models.IntegerField(default=0)  # Progress of the user in the challenge

    STATUS_CHOICES = [
        ("incomplete", "Incomplete"),
        ("complete", "Complete"),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="incomplete")  # Status of the challenge

    # Meta class for the model, including verbose names and unique constraints
    class Meta:
        verbose_name = "Achievement Members"
        verbose_name_plural = "Achievement Participants"
        unique_together = ("username", "achievementId")  # Ensure unique combination of user and challenge

    def __str__(self):
        return f"{self.username.username} - {self.achievementId.name}"  # String representation of the participant

    # Signal receiver to assign new users to existing challenges
    @receiver(post_save, sender=get_user_model())
    def assignUserToExistingAchievements(sender, instance, created, **kwargs):
        if created:
            existing_achievements = Achievement.objects.all()  # Get all existing challenges
            for achievement in existing_achievements:
                if not AchievementParticipants.objects.filter(username=instance, achievementId=achievement).exists():
                    AchievementParticipants.objects.create(
                        username=instance,
                        achievementId=achievement,
                        progress=0,
                        status="incomplete"
                    )  # Assign the new user to each existing challenge