from django.db import models

# Plant class is created to store the information of the plants
class Plant(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField(upload_to="plant_images/")
    fact = models.TextField()
    onMarket = models.BooleanField(default=True) # Boolean field to check if the plant is on market

    def __str__(self):
        return self.name # String representation of the plant

# UserGarden class is created to store the plants that the user has in their garden
class UserGarden(models.Model):
    user = models.OneToOneField("user_management.CustomUser", on_delete=models.CASCADE, primary_key=True)
    plant1Id = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True, related_name="slot1")
    plant2Id = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True, related_name="slot2")
    plant3Id = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True, related_name="slot3")
    plant4Id = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True, related_name="slot4")
    plant5Id = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True, related_name="slot5")
    plant6Id = models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True, related_name="slot6")

    def __str__(self):
        return f"{self.user.username}'s Garden"