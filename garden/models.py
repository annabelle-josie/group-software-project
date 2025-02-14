from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class userGarden(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    plant1Id = models.IntegerField(null=True, blank=True)
    plant2Id = models.IntegerField(null=True, blank=True)
    plant3Id = models.IntegerField(null=True, blank=True)
    plant4Id = models.IntegerField(null=True, blank=True)
    plant5Id = models.IntegerField(null=True, blank=True)
    plant6Id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Garden of {self.user.username}"