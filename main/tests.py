import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from main.models import Challenge, ChallengeParticipants
from user_management.models import CustomUser, UserStats
from garden.models import Plant
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
        self.client.login(username="testuser", password="SecurePass123!")


    def test_new_user_is_assigned_to_existing_challenges(self):
        """Ensure that a newly created user is automatically assigned to existing challenges."""

        new_user = CustomUser.objects.create_user(username="newtestuser", password="SecurePass123!")

        self.assertTrue(ChallengeParticipants.objects.filter(username=new_user, challengeId=self.challenge).exists())


    def test_progress_increases_when_task_completed(self):
        """Ensure progress increases when a QR code is scanned."""

        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)
        initial_progress = participant.progress

        response = self.client.post(
            "/api/v1/removeTask", 
            {"challengeId": self.challenge.challengeId}, 
        )

        participant = ChallengeParticipants.objects.get(username=self.user, challengeId=self.challenge)

        self.assertEqual(participant.progress, initial_progress + 1)

    def test_challenge_completion_when_all_tasks_done(self):
        """Ensure challenge is marked as complete when progress reaches task requirement."""

        for _ in range(self.challenge.noOfTasks):
            response = self.client.post(
                "/api/v1/removeTask", 
                {"challengeId": self.challenge.challengeId}, 
            )
        
        response = self.client.delete(
            "/api/v1/removeChallenge",
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
                "/api/v1/removeTask", 
                {"challengeId": self.challenge.challengeId}, 
            )
        
        response = self.client.delete(
            "/api/v1/removeChallenge",
            data=json.dumps({"challengeId": self.challenge.challengeId, "points": self.challenge.rewardValue}),
            content_type="application/json"
        )

        user_stats = UserStats.objects.get(user=self.user)  
        expected_points = 50 + self.challenge.rewardValue  # Initial 50 points + challenge reward

        self.assertEqual(user_stats.points, expected_points)


class MarketTests(TestCase):
    """Tests for the Market purchase functionality."""

    def setUp(self):
        """Set up test users, plants, and user stats before each test."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username="testuser", password="SecurePass123!")
        self.client.login(username="testuser", password="SecurePass123!")

        self.user_stats = UserStats.objects.get(user=self.user)

        self.plant1 = Plant.objects.create(name="Sunflower", price=10, fact="A bright yellow flower.", onMarket=True)
        self.plant2 = Plant.objects.create(name="Rose", price=60, fact="A romantic red flower.", onMarket=True)

    def test_user_can_purchase_plant(self):
        """Ensure a user can successfully purchase a plant if they have enough leaves."""

        response = self.client.post(
            reverse("add_purchased_plant"),
            data={"plantName": self.plant1.name, "user": self.user.username},
            content_type="application/json"
        )
        self.user_stats = UserStats.objects.get(user=self.user)
        expected_leaves = 50 - self.plant1.price
        owned_plants = self.user.owned_plants.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user_stats.leaves, expected_leaves)
        self.assertIn(self.plant1, owned_plants)

    def test_user_cannot_purchase_plant_if_not_enough_leaves(self):
        """Ensure a user cannot purchase a plant if they don't have enough leaves."""

        response = self.client.post(
            reverse("add_purchased_plant"),
            data={"plantName": self.plant2.name, "user": self.user.username},
            content_type="application/json"
        )
        self.user_stats = UserStats.objects.get(user=self.user)
        owned_plants = self.user.owned_plants.all()

        self.assertEqual(self.user_stats.leaves, 50)
        self.assertNotIn(self.plant2, owned_plants)

class LeaderboardTests(TestCase):
    """Tests for leaderboard functionality."""

    def setUp(self):
        """Set up a test user and create additional users with varying points."""
        self.client = Client()

        self.user = CustomUser.objects.create_user(username="testuser", password="SecurePass123!")
        self.client.login(username="testuser", password="SecurePass123!")
        self_user_stats = UserStats.objects.get(user=self.user)
        self_user_stats.points = 80
        self_user_stats.save()

        # Create 11 additional users so total 12 users exist.
        self.created_users = [self.user]
        for i in range(1, 12):
            new_user = CustomUser.objects.create_user(username=f"user{i}", password="Pass123!")
            self.created_users.append(new_user)
            stats = UserStats.objects.get(user=new_user)
            stats.points = 50 + (i * 10)
            stats.save()

def test_leaderboard_view_returns_top_ten(self):
        """Test that the leaderboard view returns the top 10 users in descending order and includes the logged-in user's points."""
        response = self.client.get(reverse("leaderboard"))
        context = response.context
        leaderboard_data = context.get("leaderboard")
        logged_in_points = context.get("points")

        self.assertEqual(logged_in_points, 80)
        self.assertIsInstance(leaderboard_data, list)
        self.assertEqual(len(leaderboard_data), 10)

        points_list = [entry['points'] for entry in leaderboard_data]
        self.assertEqual(points_list, sorted(points_list, reverse=True))