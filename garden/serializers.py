from rest_framework import serializers
from .models import userGarden

class GardenSerializer(serializers.ModelSerializer):
    class Meta:
        model = userGarden
        fields = "__all__"