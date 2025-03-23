import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from engagement.models import UserStats

custom_user = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class LeaderboardTests(TestCase):
    """Tests for leaderboard functionality."""

    def setUp(self):
        """Set up a test user and create additional users with varying points."""
        self.client = Client()

        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="SecurePass123!")
        self.client.login(username="testuser", password="SecurePass123!")
        self_user_stats = UserStats.objects.get(user=self.user)
        self_user_stats.points = 200
        self_user_stats.save()

        # Create 11 additional users so total 12 users exist.
        self.created_users = [self.user]
        for i in range(1, 12):
            new_user = custom_user.objects.create_user(username=f"user{i}", email=f"testemail{i}@email.com", password="Pass123!")
            self.created_users.append(new_user)
            stats = UserStats.objects.get(user=new_user)
            stats.points = 50 + (i * 10)
            stats.save()

    def tearDown(self):
        """Remove the temporary media directory and all its contents."""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_leaderboard_view_returns_top_ten(self):
        """Test that the leaderboard view returns the top 10 users in descending order and includes the logged-in user's points."""
        
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse("leaderboard"))
        
        self.assertIn('leaderboard', response.context)
        self.assertIn('rank', response.context)

        leaderboard_data = response.context['leaderboard']
        logged_in_rank = response.context['rank']

        self.assertEqual(logged_in_rank, 1)

        self.assertIsInstance(leaderboard_data, list)
        self.assertEqual(len(leaderboard_data), 10)

        points_list = [entry['points'] for entry in leaderboard_data]
        self.assertEqual(points_list, sorted(points_list, reverse=True))