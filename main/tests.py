from django.test import TestCase, Client
from django.urls import reverse

class HomePageTest(TestCase):
    def setUp(self):
        self.client = Client()  # Simulates a browser

    def test_homepage_loads_successfully(self):
        """Ensure the homepage loads with a 200 status code."""
        response = self.client.get(reverse('home'))  # 'home' should match your URL name in urls.py
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        """Check if the correct template is used."""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')