from django.db import models

# Create your models here.
class Challenge(models.Model):
    challengeId = models.AutoField(primary_key=True)
    title= models.CharField(max_length=50)
    desc= models.CharField(max_length=500)
    noOfTasks= models.IntegerField()
    rewardValue= models.IntegerField()

    def __str__(self):
        return self.title


class ChallengeParticipants(models.Model):
    username = models.ForeignKey("user_management.CustomUser", on_delete=models.CASCADE)
    challengeId = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    
    STATUS_CHOICES = [
        ("incomplete", "Incomplete"),
        ("complete", "Complete"),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="incomplete")

    class Meta:
        verbose_name = "Challenge Members"
        verbose_name_plural = "Challenge Participants"  
        unique_together = ("username", "challengeId")

    def __str__(self):
        return f"{self.username.username} - {self.challengeId.title}"
    
