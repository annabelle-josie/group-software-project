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
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)
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
        """Allows sending a friend request only if no rejected request exists."""
        if self == to_user:
            raise ValueError("You cannot send a friend request to yourself.")

        # Check for past requests
        existing_request = FriendRequest.objects.filter(senderId=self, receiverId=to_user).first()
        reverse_request = FriendRequest.objects.filter(senderId=to_user, receiverId=self).first()

        # If a request already exists
        if existing_request:
            if existing_request.status == "pending":
                raise ValueError("Friend request already sent.")
            elif existing_request.status == "rejected":
                raise ValueError("This user has rejected your request.")
        
        # If the reverse request was rejected, allow sending one
        if reverse_request and reverse_request.status == "rejected":
            reverse_request.delete() 

        FriendRequest.objects.create(senderId=self, receiverId=to_user)

    def accept_friend_request(self, from_user):
        """Accepts a pending friend request and deletes it while adding the friend."""
        try:
            request = FriendRequest.objects.get(senderId=from_user, receiverId=self, status="pending")
            self.friends.add(from_user)
            from_user.friends.add(self)
            request.delete()  # Remove request after accepting
        except FriendRequest.DoesNotExist:
            raise ValueError("No pending friend requests.")

    def reject_friend_request(self, from_user):
        """Rejects a pending friend request, preventing future requests from that user."""
        try:
            request = FriendRequest.objects.get(senderId=from_user, receiverId=self, status="pending")
            request.status = "rejected"
            request.save()
        except FriendRequest.DoesNotExist:
            raise ValueError("No pending friend requests.")

    def unfriend(self, friend):
        """Removes a user from friends but allows sending a new request."""
        if friend in self.friends.all():
            self.friends.remove(friend)
            friend.friends.remove(self)
        else:
            raise ValueError("This user is not your friend.")

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
            default_plant = Plant.objects.get(name="Potted Plant")  # Change "Sunflower" to your default plant
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

class FriendRequest(models.Model):
    """Model to store friend requests with a status."""
    senderId = models.ForeignKey(CustomUser, related_name="sent_requests", on_delete=models.CASCADE)
    receiverId = models.ForeignKey(CustomUser, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[
            ("pending", "Pending"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(default=now)  
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        verbose_name = "Friend Request"
        verbose_name_plural = "Friend Requests"
        unique_together = ("senderId", "receiverId") 

    def __str__(self):
        return f"{self.senderId.username} to {self.receiverId.username} ({self.status})" # Return the sender and receiver

