from django.db import models
from django.contrib.auth.models import User

class Events(models.Model):
    eventId = models.AutoField(primary_key=True)
    desc = models.TextField()
    title = models.CharField(max_length=255)
    noOfTasks = models.IntegerField()
    rewardValue = models.DecimalField()
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    eventMaster = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class EventMembers(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    eventId = models.ForeignKey(Events, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    status = models.CharField(max_length=50)

    class Meta:
        unique_together = ('username', 'eventId')

    def __str__(self):
        return f"{self.username.username} - {self.eventId.title}"