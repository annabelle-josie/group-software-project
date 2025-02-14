from rest_framework import serializers
from .models import *

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['challengeId', 'title', 'desc','noOfTasks','rewardValue']
