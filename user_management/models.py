from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Create your models here.
class UsersInfo(models.Model):
    UID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # Ensures unique PK per user
    leaves = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User Info"
        verbose_name_plural = "User Information"  

    def __str__(self):
        return f"{self.UID.username} - Points: {self.points} - Leaves: {self.leaves}"
    
@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:  # Only run when a new User is created
        UsersInfo.objects.create(UID=instance)