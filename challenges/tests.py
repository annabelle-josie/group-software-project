import json
import shutil
import tempfile
import datetime
from datetime import date, timedelta
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from challenges.models import Challenge, ChallengeParticipants
from engagement.models import UserStats

custom_user = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ChallengeTests(TestCase):
    """Tests for Challenge creation, assignment, and participation."""

    def setUp(self):
        """Set up test user and challenge before each test."""
        self.challenge1 = Challenge.objects.create(
            title="Challenge 1",
            desc="The challenge user is part of for tests.",
            noOfTasks=5,
            rewardValue=10,
            qrvalue="challenge1",
            isQR=False,
        )

        self.challenge2 = Challenge.objects.create(
            title="Challenge 2",
            desc="Not assigned to user by default.",
            noOfTasks=5,
            rewardValue=10,
            qrvalue="challenge2",
            isQR=True,
        )

        self.challenge3 = Challenge.objects.create(
            title="Challenge 3",
            desc="Not assigned to user by default.",
            noOfTasks=5,
            rewardValue=10,
            qrvalue="challenge3",
            isQR=False,
        )

        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com",password="SecurePass123!")

        self.participant = ChallengeParticipants.objects.create(
            username=self.user,
            challengeId=self.challenge1,
            progress=0,
            status="incomplete",
            date=timezone.now().date()
        )
        self.client.login(username="testuser", password="SecurePass123!")

    def tearDown(self):
        """Remove the temporary media directory and all its contents."""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_progress_increases_when_task_completed(self):
        """Ensure progress increases when a QR code is scanned."""
        response = self.client.post(
            reverse("challenge_increment_progress", args=[self.challenge1.challengeId]),
            data=json.dumps({"challengeId": self.challenge1.challengeId}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        # Use the model manager and correct field name 'challengeId'
        updated_participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge1)
        self.assertEqual(updated_participant.progress, 1)

    def test_challenge_completion_when_all_tasks_done(self):
        """Ensure challenge is marked as complete when progress reaches task requirement."""
        for _ in range(self.challenge1.noOfTasks):
            response = self.client.post(
                reverse("challenge_increment_progress", args=[self.challenge1.challengeId]),
                data=json.dumps({"challengeId": self.challenge1.challengeId}),
                content_type="application/json"
            )
        
        response = self.client.delete(
            "/challenges/api/v1/removeChallenge",
            data=json.dumps({"challengeId": self.challenge1.challengeId, "points": self.challenge1.rewardValue}),
            content_type="application/json"
        )
        updated_participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_participant.status, "complete")

    def test_only_gamekeepers_can_access_challenges_page(self):
        """Test that only game keepers can access the challenges page."""
 
        gamekeeper = custom_user.objects.create_user(username="gamekeeper", email="gamekeeper@email.com", password="SecurePass123!")
        gk_group, _ = Group.objects.get_or_create(name="Game Keepers")
        gamekeeper.groups.add(gk_group)
        gamekeeper.save()

        response = self.client.get(reverse("allchallenges"))
        self.assertEqual(response.status_code, 302)

        self.client.logout()
        self.client.login(username="gamekeeper", password="SecurePass123!")
        response = self.client.get(reverse("allchallenges"))
        self.assertEqual(response.status_code, 200)

    def test_assign_three_new_challenges_daily(self):
        """Test if user receives 3 new challenges every day."""
        self.client.login(username="testuser", password="SecurePass123!")
        
        day1 = date.today()
        day2 = day1 + timedelta(days=1)
        
        # Day 1 Simulation
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime.datetime.combine(day1, datetime.time.min)
            response1 = self.client.get(reverse("home"))
            self.assertEqual(response1.status_code, 200)

        day1_challenges = ChallengeParticipants.objects.filter(username=self.user, date=day1, status="incomplete")
        self.assertEqual(day1_challenges.count(), 3)

        completed_challenge = day1_challenges.first()
        completed_challenge.status = "complete"
        completed_challenge.save()

        day1_active = ChallengeParticipants.objects.filter(username=self.user, date=day1, status="incomplete")
        self.assertEqual(day1_active.count(), 2)
        
        # Day 2 Simulation
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = datetime.datetime.combine(day2, datetime.time.min)
            response2 = self.client.get(reverse("home"))
            self.assertEqual(response2.status_code, 200)

        day2_challenges = ChallengeParticipants.objects.filter(username=self.user, date=day2, status="incomplete")
        self.assertEqual(day2_challenges.count(), 3)

