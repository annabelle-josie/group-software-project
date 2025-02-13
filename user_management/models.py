from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Custom User model that extends Django's built-in User model."""
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)
    
    # Merging UsersInfo fields here
    leaves = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def send_friend_request(self, to_user):
        if self == to_user:
            raise ValueError("You cannot send a friend request to yourself.")
        if self.friends.filter(pk=to_user.pk).exists():
            raise ValueError("You are already friends.")
        if FriendRequest.objects.filter(senderId=self, receiverId=to_user, status="pending").exists():
            raise ValueError("Friend request already sent.")
        if FriendRequest.objects.filter(senderId=to_user, receiverId=self, status="pending").exists():
            raise ValueError("User has already sent you a friend request.")

        FriendRequest.objects.create(senderId=self, receiverId=to_user)

    def accept_friend_request(self, from_user):
        try:
            request = FriendRequest.objects.get(senderId=from_user, receiverId=self, status="pending")
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
            request = FriendRequest.objects.get(senderId=from_user, receiverId=self, status="pending")
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
