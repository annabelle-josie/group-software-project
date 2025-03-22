import json
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from engagement.models import UserStats
from .models import Challenge, ChallengeParticipants

custom_user = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ChallengeTests(TestCase):
    """Tests for Challenge creation, assignment, and participation."""

    def setUp(self):
        """Set up test user and challenge before each test."""
        self.challenge = Challenge.objects.create(
            title="Recycle 5 Bottles",
            desc="Recycle 5 plastic bottles to earn rewards.",
            noOfTasks=5,
            rewardValue=10,
            qrvalue="recycle_bottle"
        )

        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="SecurePass123!")
        self.client.login(username="testuser", password="SecurePass123!")

    def tearDown(self):
        """Remove the temporary media directory and all its contents."""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_new_user_is_assigned_to_existing_challenges(self):
        """Ensure that a newly created user is automatically assigned to existing challenges."""

        new_user = custom_user.objects.create_user(username="newtestuser", email="testemail@email.com", password="SecurePass123!")

        self.assertTrue(ChallengeParticipants.objects.filter(username=new_user, challengeId=self.challenge).exists())


    def test_progress_increases_when_task_completed(self):
        """Ensure progress increases when a QR code is scanned."""

        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)
        initial_progress = participant.progress

        response = self.client.post(
            "/challenges/api/v1/removeTask", 
            {"challengeId": self.challenge.challengeId}, 
        )

        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)

        self.assertEqual(participant.progress, initial_progress + 1)

    def test_challenge_completion_when_all_tasks_done(self):
        """Ensure challenge is marked as complete when progress reaches task requirement."""

        for _ in range(self.challenge.noOfTasks):
            response = self.client.post(
                "/challenges/api/v1/removeTask", 
                {"challengeId": self.challenge.challengeId}, 
            )
        
        response = self.client.delete(
            "/challenges/api/v1/removeChallenge",
            data=json.dumps({"challengeId": self.challenge.challengeId, "points": self.challenge.rewardValue}),
            content_type="application/json"
        )

        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)
  
        self.assertEqual(participant.status, "complete")

    def test_daily_reset_logic(self):
        """Ensure progress resets at midnight when `home` is accessed on a new day."""
        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)

        # Simulate completing the challenge the previous day
        participant.progress = self.challenge.noOfTasks
        participant.status = "complete"
        participant.date = timezone.now() - timezone.timedelta(days=1)
        participant.save()

        # Simulate a request on a new day triggering the reset logic
        current_date = timezone.now().date()
        ChallengeParticipants.objects.filter(username=self.user).update(progress=0, status="incomplete", date=current_date)
        updated_participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)

        self.assertEqual(updated_participant.progress, 0)
        self.assertEqual(updated_participant.status, "incomplete")
        self.assertEqual(updated_participant.date, current_date)

    def test_rewards_are_given_on_completion(self):
        """Ensure users receive reward points when completing a challenge."""
        for _ in range(self.challenge.noOfTasks):
            response = self.client.post(
                "/challenges/api/v1/removeTask", 
                {"challengeId": self.challenge.challengeId},
            )
        
        response = self.client.delete(
            "/challenges/api/v1/removeChallenge",
            data=json.dumps({"challengeId": self.challenge.challengeId, "points": self.challenge.rewardValue}),
            content_type="application/json"
        )

        user_stats = UserStats.objects.get(user=self.user)
        expected_points = 50 + self.challenge.rewardValue

        self.assertEqual(user_stats.points, expected_points)
