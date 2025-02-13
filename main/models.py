from django.db import models

# Create your models here.
class Challenge(models.Model):
    challengeId = models.AutoField(primary_key=True)
    title= models.CharField(max_length=50)
    desc= models.CharField(max_length=50)
    noOfTasks= models.IntegerField()
    rewardValue= models.IntegerField()

    def __str__(self):
        return self.title

