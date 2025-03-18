from django.core.management.base import BaseCommand
from challenges.models import Challenge
import secrets
import string

CHALLENGE_DATA = [
    {
        "title": "Thanks for Logging In",
        "desc": "Thank you for checking in today! Here's a bonus for being active.",
        "noOfTasks": 1,
        "rewardValue": 20,
        "isQR": False,
        "repeatable": True,
    },
    {
        "title": "Recycle 3 Pieces of Litter",
        "desc": "Pick up at least 3 pieces of litter and take it to a campus recycling bin and scan the QR code posted there.",
        "noOfTasks": 3,
        "rewardValue": 20,
        "isQR": True,
        "repeatable": True,
    },
    {
        "title": "Bring Your Reusable Water Bottle",
        "desc": "Use a reusable water bottle throughout the day and scan the QR code at the water fountain.",
        "noOfTasks": 1,
        "rewardValue": 15,
        "isQR": True,
        "repeatable": True,
    },
    {
        "title": "Bring Your Own Bag",
        "desc": "Bring a reusable shopping bag to campus and use it when you shop. Ask for the QR code at the Marketplace to verify.",
        "noOfTasks": 1,
        "rewardValue": 15,
        "isQR": True,
        "repeatable": True,
    },
    {
        "title": "Bike to Campus",
        "desc": "Ride your bicycle to campus and scan the QR code at the bike shed.",
        "noOfTasks": 1,
        "rewardValue": 25,
        "isQR": True,
        "repeatable": True,
    },
    {
        "title": "Opt to Walk",
        "desc": "Consider walking to wherever you need to go today.",
        "noOfTasks": 1,
        "rewardValue": 5,
        "isQR": False,
        "repeatable": True,
    },
    {
        "title": "Conserve Energy",
        "desc": "Remember to turn off unnecessary devices and lights around you.",
        "noOfTasks": 1,
        "rewardValue": 5,
        "isQR": False,
        "repeatable": True,
    },
    {
        "title": "Eat Sustainably",
        "desc": "Consider reducing your meat consumption today to help lower your carbon footprint.",
        "noOfTasks": 1,
        "rewardValue": 5,
        "isQR": False,
        "repeatable": True,
    }
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        for challenge_info in CHALLENGE_DATA:
            if challenge_info.get("isQR"):
                challenge_info["qrvalue"] = ''.join(
                    secrets.choice(string.ascii_letters + string.digits) for _ in range(20)
                )
            else:
                challenge_info["qrvalue"] = None

            challenge_obj, created = Challenge.objects.get_or_create(
                title=challenge_info["title"],
                defaults=challenge_info
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created challenge: {challenge_obj.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Challenge already exists: {challenge_obj.title}"))