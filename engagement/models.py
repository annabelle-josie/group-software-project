from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


class UserStats(models.Model):
    """Model to store user stats like leaves and points."""
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name="stats")
    leaves = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User Stats"
        verbose_name_plural = "User Stats"

    def __str__(self):
        return f"| {self.user.username} | {self.leaves} Leaves Remaining | {self.points} Total Points |"
    

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
    url = models.CharField(max_length=200, blank=True, null=True, default=None)

    def __str__(self):
        return self.name
    
class AchievementParticipants(models.Model):
    username = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)  # Reference to the user
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