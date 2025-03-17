from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, Group, BaseUserManager

class CustomUserManager(BaseUserManager):
    """Custom manager to prevent issues with swapped user models."""
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and return a regular user with the given username and password."""
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and return a superuser with the given username and password via create_user function."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(username, email, password, **extra_fields)
        group, created = Group.objects.get_or_create(name="Game Keepers")
        user.groups.add(group)
        return user
    
class CustomUser(AbstractUser):
    """Custom user model extending the default Django user model with friends, owned plants, and stats."""
    email = models.EmailField(null=False, blank=False)
    owned_plants = models.ManyToManyField("plants.Plant", related_name="owners")
    objects = CustomUserManager()

    def send_friend_request(self, to_user):
        """Send a friend request to another user, with a lot of cases covered."""
        if self == to_user:
            raise ValueError("You cannot send a friend request to yourself.")

        existing_request = Friendship.objects.filter(user1=self, user2=to_user).first()
        reverse_request = Friendship.objects.filter(user1=to_user, user2=self).first()

        # CASE 1: Sender has been previously rejected → Do nothing
        if existing_request and existing_request.status == "rejected":
            return

        # CASE 2: Recipient had rejected but now sends a request → Remove old record and create a new one.
        if reverse_request and reverse_request.status == "rejected":
            reverse_request.delete()
            Friendship.objects.create(user1=self, user2=to_user, status="pending")
            return
        
        # CASE 3: If there's already a pending request from the recipient, accept it.
        if reverse_request and reverse_request.status == "pending":
            reverse_request.status = "accepted"
            reverse_request.save()
            return

        # CASE 4: New Request
        if not existing_request:
            Friendship.objects.create(user1=self, user2=to_user, status="pending")
        else:
            raise ValueError("Friend request already sent or accepted.")


    def accept_friend_request(self, from_user):
        """Accepts a pending friend request and updates the status."""
        try:
            friendship = Friendship.objects.get(user1=from_user, user2=self, status="pending")
            friendship.status = "accepted"
            friendship.save()
        except Friendship.DoesNotExist:
            raise ValueError("No pending friend request from this user.")

    def reject_friend_request(self, from_user):
        """Rejects a pending friend request."""
        try:
            friendship = Friendship.objects.get(user1=from_user, user2=self, status="pending")
            friendship.status = "rejected"
            friendship.save()
        except Friendship.DoesNotExist:
            raise ValueError("No pending friend request from this user.")

    def unfriend(self, friend):
        """Removes a friend from the user's friends list."""
        friendship = Friendship.objects.filter(
            (models.Q(user1=self, user2=friend) | models.Q(user1=friend, user2=self)),
            status="accepted"
        )
        
        if friendship.exists():
            friendship.delete()
            return True
        return False

    def get_friends(self):
        """Returns a queryset of all accepted friends, including their garden and plants."""
        friends = Friendship.objects.filter(
            models.Q(user1=self, status="accepted") | models.Q(user2=self, status="accepted")
        ).values_list("user1", "user2")

        friend_ids = [user_id for pair in friends for user_id in pair if user_id != self.id]
        
        return CustomUser.objects.filter(id__in=friend_ids).select_related('usergarden')

    
    def get_incoming_friend_requests(self):
        """Returns a queryset of friend requests that were sent to the user."""
        request_ids = Friendship.objects.filter(
            user2=self, status="pending"
        ).values_list("user1", flat=True)

        return CustomUser.objects.filter(id__in=request_ids)

class Friendship(models.Model):
    """Model to track friendships explicitly, replacing the ManyToManyField."""
    user1 = models.ForeignKey(CustomUser, related_name="friendship_initiated", on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, related_name="friendship_received", on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(default=now)  
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        verbose_name = "Friendship"
        verbose_name_plural = "Friendships"
        unique_together = ("user1", "user2")  # Ensure unique pairs

    def __str__(self):
        return f"{self.user1.username} -> {self.user2.username} ({self.status})"

