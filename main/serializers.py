from rest_framework import serializers
from .models import *

class gardenSerializer(serializers.ModelSerializer):
    class Meta:
        model = userGarden
        fields = ['username','plant1Id', 'plant2Id', 'plant3Id','plant4Id', 'plant5Id', 'plant6Id' ]