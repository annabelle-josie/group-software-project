from rest_framework import serializers
from .models import Challenge

# Serialiser for the Challenge model
class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge  # Specify the model to be serialised
        fields = ['challengeId', 'title', 'desc', 'noOfTasks', 'rewardValue', 'isQR']  # Fields to include in the serialisation