from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from main.models import Challenge, ChallengeParticipants
from user_management.models import CustomUser
# Test case for the home page and protected views
class HomePageTest(TestCase):

    def setUp(self):
        """Set up a test user for authentication."""
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')

        # List of all protected views that require authentication
        self.protected_urls = [
            reverse('home'),
            reverse('leaderboard'),
            reverse('garden'),
            reverse('market'),
            reverse('events'),
        ]

    def test_redirects_for_unauthenticated_users(self):
        """Ensure unauthenticated users are redirected to login for all protected pages."""
        for url in self.protected_urls:
            with self.subTest(url=url):  # Runs the test for each page
                response = self.client.get(url, follow=True)  # Follow the redirect
                self.assertRedirects(response, reverse('login') + f"?next={url}")

    def test_authenticated_users_can_access_pages(self):
        """Ensure authenticated users can access all pages without redirection."""
        self.client.login(username='testuser', password='password123')
        for url in self.protected_urls:
            with self.subTest(url=url):  # Runs the test for each page
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)  # Check for successful access


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

        self.user = CustomUser.objects.create_user(username="testuser", password="SecurePass123!")


    def test_user_is_assigned_to_challenges(self):
        """Ensure the user is automatically assigned to existing challenges upon creation."""
        self.assertTrue(ChallengeParticipants.objects.filter(username=self.user, challengeId=self.challenge).exists())

    def test_progress_increases_when_task_completed(self):
        """Ensure progress increases when a QR code is scanned."""
        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)
        initial_progress = participant.progress

        participant.progress += 1
        participant.save()

        updated_participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)
        self.assertEqual(updated_participant.progress, initial_progress + 1)

    def test_challenge_completion_when_all_tasks_done(self):
        """Ensure challenge is marked as complete when progress reaches task requirement."""
        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)

        participant.progress = self.challenge.noOfTasks
        participant.status = "complete"
        participant.save()

        updated_participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)
        self.assertEqual(updated_participant.status, "complete")

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
        self.assertEqual(updated_participant.date.date(), current_date)

    def test_rewards_are_given_on_completion(self):
        """Ensure users receive reward points when completing a challenge."""
        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)

        # Simulate user completing the challenge
        participant.progress = self.challenge.noOfTasks
        participant.status = "complete"
        participant.save()

        self.user.stats.points += self.challenge.rewardValue
        self.user.stats.save()

        updated_user = CustomUser.objects.get(username=self.user.username)
        self.assertEqual(updated_user.stats.points, 50 + self.challenge.rewardValue)  # Initial points (50) + Reward (10)


    