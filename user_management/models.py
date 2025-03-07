from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, Group, BaseUserManager

from django.db.models.signals import post_save
from django.dispatch import receiver

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
        return self.create_user(username, email, password, **extra_fields)
    
class CustomUser(AbstractUser):
    """Custom user model extending the default Django user model with friends, owned plants, and stats."""
    email = models.EmailField(null=True, blank=True) # TODO: Allows no email, potentially remove in sprint 2
    owned_plants = models.ManyToManyField("garden.Plant", related_name="owners")
    objects = CustomUserManager()

    def is_game_keeper(self):
        """Check if the user belongs to the 'Game Keepers' group."""
        return self.groups.filter(name="Game Keepers").exists()

    def award_points_and_leaves(self, target_user, amount):
        """Allows Game Keepers to award points and leaves to other users."""
        if not self.is_game_keeper():
            raise PermissionError("Only Game Keepers can award points or leaves.")

        target_user.stats.points += amount
        target_user.stats.leaves += amount
        target_user.stats.save()

    def send_friend_request(self, to_user):
        """Send a friend request unless the sender was already rejected. If recipient sends a request, remove restriction."""
        if self == to_user:
            raise ValueError("You cannot send a friend request to yourself.")

        # Check if a request already exists in either direction
        existing_request = Friendship.objects.filter(user1=self, user2=to_user).first()
        reverse_request = Friendship.objects.filter(user1=to_user, user2=self).first()

        # CASE 1: Sender has been previously rejected → Cannot send again
        if existing_request and existing_request.status == "rejected":
            return

        # CASE 2: Recipient had rejected but now sends a request → Remove restriction
        if reverse_request and reverse_request.status == "rejected":
            reverse_request.status = "pending"
            reverse_request.save()
            return

        # CASE 3: New Request
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
        """Returns a queryset of all accepted friends."""
        friends = Friendship.objects.filter(
            models.Q(user1=self, status="accepted") | models.Q(user2=self, status="accepted")
        ).values_list("user1", "user2")

        friend_ids = [user_id for pair in friends for user_id in pair if user_id != self.id]
        return CustomUser.objects.filter(id__in=friend_ids)
    
    def get_incoming_friend_requests(self):
        """Returns a queryset of all friend requests."""
        friends = Friendship.objects.filter(
            models.Q(user1=self, status="pending") | models.Q(user2=self, status="pending")
        ).values_list("user1", "user2")

        request_ids = [user_id for pair in friends for user_id in pair if user_id != self.id]
        return CustomUser.objects.filter(id__in=request_ids)


def ensure_game_keeper_group():
    """Creates the 'Game Keepers' group if it doesn't exist."""
    Group.objects.get_or_create(name="Game Keepers")

class UserStats(models.Model):
    """Model to store user stats like leaves and points."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="stats")
    leaves = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    class Meta:
        verbose_name = "User Stats"
        verbose_name_plural = "User Stats"

    def __str__(self):
        return f"| {self.user.username} | {self.leaves} Leaves Remaining | {self.points} Total Points |"

@receiver(post_save, sender=CustomUser)
def create_user_stats(sender, instance, created, **kwargs):
    """Automatically creates a UserStats entry for every new user."""
    if created:
        UserStats.objects.create(user=instance, leaves=50, points=50)

@receiver(post_save, sender=CustomUser)
def create_userGarden(sender, instance, created, **kwargs):
    """Automatically creates a UserGarden for every new user."""
    if created:
        from garden.models import UserGarden, Plant  # Prevent circular imports
        
        try:
            default_plant = Plant.objects.get(name="Potted Plant")  
        except Plant.DoesNotExist:
            default_plant = None  # If the plant isn't found, leave slots empty
        
        # Create the UserGarden with the default plant in all six slots
        UserGarden.objects.create(
            user=instance,
            plant1Id=default_plant,
            plant2Id=default_plant,
            plant3Id=default_plant,
            plant4Id=default_plant,
            plant5Id=default_plant,
            plant6Id=default_plant,
        )

        # Also add this plant to the owned plants list
        if default_plant:
            instance.owned_plants.add(default_plant)

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

