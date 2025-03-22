import shutil
import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

custom_user = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class HomePageTest(TestCase):

    def setUp(self):
        """Set up a test user for authentication."""
        
        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="password123")

        # List of all protected views that require authentication
        self.protected_urls = [
            reverse('home'),
            reverse('friends'),
            reverse('challenges'),
            reverse('events'),
            reverse('market'),
            reverse('leaderboard'),
            reverse('settings'),
        ]

    def tearDown(self):
        """Remove the temporary media directory and all its contents."""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

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