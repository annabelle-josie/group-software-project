from django.core.management.base import BaseCommand
from engagement.models import Achievement

class Command(BaseCommand):
    help = "Creates predefined achievements"

    def handle(self, *args, **kwargs):
        achievements = [
            {"name": "Point Scorer I", "desc": "Score points", "amount": 100, "rewardValue": 10, "type": "onPointGain"},
            {"name": "Point Scorer II", "desc": "Score points", "amount": 500, "rewardValue": 50, "type": "onPointGain"},
            {"name": "Point Scorer III", "desc": "Score points", "amount": 2500, "rewardValue": 250, "type": "onPointGain"},
            {"name": "Event Completer I", "desc": "Complete events", "amount": 5, "rewardValue": 50, "type": "onEventComplete"},
            {"name": "Event Completer II", "desc": "Complete events", "amount": 25, "rewardValue": 100, "type": "onEventComplete"},
            {"name": "Event Completer III", "desc": "Complete events", "amount": 100, "rewardValue": 150, "type": "onEventComplete"},
            {"name": "Challenge Completer I", "desc": "Complete challenges", "amount": 50, "rewardValue": 50, "type": "onChallengeComplete"},
            {"name": "Challenge Completer II", "desc": "Complete challenges", "amount": 250, "rewardValue": 100, "type": "onChallengeComplete"},
            {"name": "Challenge Completer III", "desc": "Complete challenges", "amount": 1000, "rewardValue": 150, "type": "onChallengeComplete"},
            {"name": "Resource Explorer", "desc": "Visit the Exeter Uni sustainability page", "amount": 1, "rewardValue": 30, "type": "onVisitSite", "url": " https://www.exeter.ac.uk/about/sustainability/"},
        ]
        
        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data["name"],
                defaults=achievement_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created {achievement.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"{achievement.name} already exists"))
