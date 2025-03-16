from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from users.models import UserStats

custom_user = get_user_model()

# Defines the demo users and the desired points/leaves.
DEMO_USERS = [
    {
        "username": "Jason",
        "email": "jg988@exeter.ac.uk",
        "password": "password1",
        "points": 50,
    },
    {
        "username": "Andy",
        "email": "at969@exeter.ac.uk",
        "password": "password2",
        "points": 130,
    },
    {
        "username": "Annabelle",
        "email": "ar999@exeter.ac.uk",
        "password": "password3",
        "points": 70,
    },
    {
        "username": "Amy",
        "email": "al980@exeter.ac.uk",
        "password": "password4",
        "points": 80,
    },
    {
        "username": "David",
        "email": "dw689@exeter.ac.uk",
        "password": "password5",
        "points": 90,
    },
    {
        "username": "Oliver",
        "email": "oj261@exeter.ac.uk",
        "password": "password6",
        "points": 100,
    },
    {
        "username": "James",
        "email": "jb1658@exeter.ac.uk",
        "password": "password7",
        "points": 110,
    },
]

class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            for user_data in DEMO_USERS:
                username = user_data["username"]
                email = user_data["email"]
                password = user_data["password"]
                points = user_data["points"]

                user, created = custom_user.objects.get_or_create(username=username, defaults={"email": email})
                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
                else:
                    self.stdout.write(self.style.WARNING(f"User {username} already exists."))
                
                stats, stats_created = UserStats.objects.get_or_create(user=user)
                stats.points = points
                stats.leaves = points
                stats.save()
                if stats_created:
                    self.stdout.write(self.style.SUCCESS(f"Created UserStats for {username} with {points} points/leaves."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated UserStats for {username} to {points} points/leaves."))

            self.stdout.write(self.style.SUCCESS("Created/updated successfully."))