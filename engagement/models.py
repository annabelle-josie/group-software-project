from django.db import models

class UserStats(models.Model):
    """Model to store user stats like leaves and points."""
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE, related_name="stats")
    leaves = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    class Meta:
        verbose_name = "User Stats"
        verbose_name_plural = "User Stats"

    def __str__(self):
        return f"| {self.user.username} | {self.leaves} Leaves Remaining | {self.points} Total Points |"