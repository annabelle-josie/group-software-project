from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import ModelForm

# Model representing a challenge
class Challenge(models.Model):
    challengeId = models.AutoField(primary_key=True)  # Primary key for the challenge
    title = models.CharField(max_length=50)  # Title of the challenge
    desc = models.CharField(max_length=500)  # Description of the challenge
    noOfTasks = models.IntegerField()  # Number of tasks in the challenge
    rewardValue = models.IntegerField()  # Reward value for completing the challenge

    def __str__(self):
        return self.title  # String representation of the challenge

# Form for creating or updating a challenge
class challengeForm(ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'desc', 'noOfTasks', 'rewardValue']  # Fields to include in the form

# Model representing participants in a challenge
class ChallengeParticipants(models.Model):
    username = models.ForeignKey("user_management.CustomUser", on_delete=models.CASCADE)  # Reference to the user
    challengeId = models.ForeignKey(Challenge, on_delete=models.CASCADE)  # Reference to the challenge
    progress = models.IntegerField(default=0)  # Progress of the user in the challenge

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
@receiver(post_save, sender=User)
def assign_user_to_existing_challenges(sender, instance, created, **kwargs):
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