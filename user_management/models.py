from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Create your models here.
class UsersInfo(models.Model):
    Username = models.OneToOneField(User, to_field="username", on_delete=models.CASCADE, primary_key=True)
    Leaves = models.IntegerField(default=0)
    Points = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User Info"
        verbose_name_plural = "User Information"  

    def __str__(self):
        return f"{self.Username.username} - Points: {self.Points} - Leaves: {self.Leaves}"
    
@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:  # Only run when a new User is created
        UsersInfo.objects.create(Username=instance)

    