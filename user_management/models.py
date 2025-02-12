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

    


class FriendRequest(models.Model):
    senderId = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    receiverId = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ("senderId", "receiverId")  

    def __str__(self):
        return f"{self.senderId.username} to {self.receiverId.username} ({self.status})"
    

def send_friend_request(self, to_user):
    if self == to_user:
        raise ValueError("You cannot send a friend request to yourself.")

    if self.friends.filter(pk=to_user.pk).exists():
        raise ValueError("You are already friends.")

    if FriendRequest.objects.filter(from_user=self, to_user=to_user, status="pending").exists():
        raise ValueError("Friend request already sent.")

    if FriendRequest.objects.filter(from_user=to_user, to_user=self, status="pending").exists():
        raise ValueError("User has already sent you a friend request.")

    FriendRequest.objects.create(from_user=self, to_user=to_user)
    

def accept_friend_request(self, from_user):
    try:
        request = FriendRequest.objects.get(from_user=from_user, to_user=self, status="pending")

        if self.friends.filter(pk=from_user.pk).exists():
            raise ValueError("You are already friends.")

        request.status = "accepted"
        request.save()

        self.friends.add(from_user)
        from_user.friends.add(self)
    except FriendRequest.DoesNotExist:
        raise ValueError("No pending friend requests.")

def reject_friend_request(self, from_user):
    try:
        request = FriendRequest.objects.get(from_user=from_user, to_user=self, status="pending")
        request.status = "rejected"
        request.save()
    except FriendRequest.DoesNotExist:
        raise ValueError("No pending friend requests.")

def remove_friend(self, friend):
    if friend in self.friends.all():
        self.friends.remove(friend)
        friend.friends.remove(self)  
    else:
        raise ValueError("This user is not your friend.")


