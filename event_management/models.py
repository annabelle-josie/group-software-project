from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from io import BytesIO
from django.core.files.base import ContentFile

# Model representing an event
class Events(models.Model):
    eventId = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=500)
    title = models.CharField(max_length=50)
    noOfTasks = models.IntegerField()
    rewardValue = models.IntegerField()
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    eventQR = models.CharField(max_length=100, default=None, null=True, blank=True)  
    eventQRImage = models.ImageField(upload_to="qr_codes/", default=None, null=True, blank=True)  
    isQR = models.BooleanField(default=False) 
    eventImage = models.ImageField(upload_to="event_images/", default=None, null=True, blank=True)  
    eventMaster = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Events"
        verbose_name_plural = "Events"  

    def __str__(self):
        return self.title # String representation of the event
    
    def save(self, *args, **kwargs):
        if not self.eventImage:
            self.eventImage = "default_event_images/cheese.jpg"
        super().save(*args, **kwargs)

# Model representing the participants of an event
class EventParticipants(models.Model):
    username = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE) # Reference to the user
    eventId = models.ForeignKey(Events, on_delete=models.CASCADE) # Reference to the event
    progress = models.IntegerField(default=0) # Progress of the user in the event
    STATUS_CHOICES = [
        ("incomplete", "Incomplete"),
        ("complete", "Complete"),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="incomplete") # Status of the event
    
    class Meta:
        verbose_name = "Event Members"
        verbose_name_plural = "Event Participants"  
        unique_together = ("username", "eventId") # Ensure unique combination of username and eventId

    def __str__(self):
        return f"{self.username.username} - {self.eventId.title}" # String representation of the event participant

    def incrementProgress(self):
        if self.progress < self.eventId.noOfTasks:
            self.progress += 1
        if self.progress == self.eventId.noOfTasks:
            self.status = "complete"
        self.save()

