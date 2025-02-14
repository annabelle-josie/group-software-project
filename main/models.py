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

# class userGarden(models.Model):
#     username= models.AutoField(primary_key=True)
#     plant1Id= models.ForeignKey(plants,on_delete=models.CASCADE)
#     plant2Id= models.ForeignKey(plants,on_delete=models.CASCADE)
#     plant3Id= models.ForeignKey(plants,on_delete=models.CASCADE)
#     plant4Id= models.ForeignKey(plants,on_delete=models.CASCADE)
#     plant5Id= models.ForeignKey(plants,on_delete=models.CASCADE)
#     plant6Id= models.ForeignKey(plants,on_delete=models.CASCADE)
#     def __str__(self):
#             return self.username