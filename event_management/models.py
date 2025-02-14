from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Events(models.Model):
    eventId = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=500)
    title = models.CharField(max_length=50)
    noOfTasks = models.IntegerField()
    rewardValue = models.IntegerField()
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    eventMaster = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Events"
        verbose_name_plural = "Events"  

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save to assign all users to a newly created event"""
        is_new = self.pk is None  # Check if this is a new event
        super().save(*args, **kwargs)  # Save the event first

        if is_new:
            # Assign all existing users to this event
            all_users = User.objects.all()
            for user in all_users:
                EventParticipants.objects.create(
                    username=user,
                    eventId=self,
                    progress=0,
                    status="incomplete"
                )

class EventParticipants(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    eventId = models.ForeignKey(Events, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    STATUS_CHOICES = [
        ("incomplete", "Incomplete"),
        ("complete", "Complete"),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="incomplete")
    
    class Meta:
        verbose_name = "Event Members"
        verbose_name_plural = "Event Participants"  

    def __str__(self):
        return f"{self.username.username} - {self.eventId.title}"

# Automatically assign new users to all existing events
@receiver(post_save, sender=User)
def assign_user_to_existing_events(sender, instance, created, **kwargs):
    if created:  # Runs only when a new user is created
        existing_events = Events.objects.all()
        for event in existing_events:
            EventParticipants.objects.create(
                username=instance,
                eventId=event,
                progress=0,
                status="incomplete"
            )
