from rest_framework import serializers
from .models import Plant, UserGarden

# PlantSerializer class is created to serialize the Plant model
class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ["id", "name", "price", "image", "fact"]

# UserGardenSerializer class is created to serialize the UserGarden model
class UserGardenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGarden
        fields = "__all__"