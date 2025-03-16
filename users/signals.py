from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from garden.utils import get_or_create_default_plant
from engagement.models import UserStats
from garden.models import UserGarden, Plant

custom_user = get_user_model()

@receiver(post_save, sender=custom_user)
def create_user_stats(sender, instance, created, **kwargs):
    """Automatically creates a UserStats entry for every new user."""
    if created:
        UserStats.objects.create(user=instance, leaves=50, points=50)

@receiver(post_save, sender=custom_user)
def create_userGarden(sender, instance, created, **kwargs):
    """Automatically creates a UserGarden for every new user."""
    if created:
        try:
            default_plant = get_or_create_default_plant()
        except Plant.DoesNotExist:
            default_plant = None


        UserGarden.objects.create(
            user=instance,
            plant1Id=default_plant,
            plant2Id=default_plant,
            plant3Id=default_plant,
            plant4Id=default_plant,
            plant5Id=default_plant,
            plant6Id=default_plant
            
        )
        
        if default_plant:
            instance.owned_plants.add(default_plant)