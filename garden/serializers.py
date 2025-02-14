from rest_framework import serializers
from .models import Plant, UserGarden

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ["id", "name", "price", "image", "fact"]

class UserGardenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGarden
        fields = "__all__"