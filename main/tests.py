from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from engagement.models import UserStats
from garden.models import Plant

custom_user = get_user_model()
# Test case for the home page and protected views
class HomePageTest(TestCase):

    def setUp(self):
        """Set up a test user for authentication."""
        
        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="password123")

        # List of all protected views that require authentication
        self.protected_urls = [
            reverse('home'),
            reverse('friends'),
            reverse('events'),
            reverse('leaderboard'),
            reverse('market'),
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


class MarketTests(TestCase):
    """Tests for the Market purchase functionality."""

    def setUp(self):
        """Set up test users, plants, and user stats before each test."""
        self.client = Client()
        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="SecurePass123!")
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
