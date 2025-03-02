from django.test import TestCase, Client
from django.urls import reverse
from user_management.models import CustomUser
from garden.models import UserGarden, Plant

class GardenTests(TestCase):
    """Tests for User Garden and Plant functionality."""

    def setUp(self):
        """Set up test users, plants, and gardens before each test."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(username="testuser", password="SecurePass123!")
        self.client.login(username="testuser", password="SecurePass123!")

        self.plant1 = Plant.objects.create(name="Sunflower", price=10, fact="A bright yellow flower.")
        self.plant2 = Plant.objects.create(name="Rose", price=15, fact="A romantic red flower.")
        self.unowned_plant = Plant.objects.create(name="Cactus", price=20, fact="A desert plant.")

        self.user.owned_plants.add(self.plant1, self.plant2)
        self.garden = UserGarden.objects.get(user=self.user)

    def test_owned_plants_can_be_placed_in_garden(self):
        """Ensure only owned plants can be placed in the garden."""
        response = self.client.post(
            reverse("updateGarden"),  # Ensure correct name is used in `urls.py`
            {"plantname": self.plant1.name, "slot": 1}
        )

        self.garden = UserGarden.objects.get(user=self.user)

        self.assertEqual(response.status_code, 302)  # Redirect expected on success
        self.assertEqual(self.garden.plant1Id, self.plant1)

    def test_garden_update_correctly_saves_plant(self):
        """Ensure updating a garden slot correctly saves the plant."""
        self.client.post(
            reverse("updateGarden"),
            {"plantname": self.plant2.name, "slot": 3}
        )

        self.garden = UserGarden.objects.get(user=self.user)

        self.assertEqual(self.garden.plant3Id, self.plant2)

