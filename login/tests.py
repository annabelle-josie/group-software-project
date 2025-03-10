from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

custom_user = get_user_model() # Get the user model

class LoginTests(TestCase):
    """Tests for user authentication including signup, login, and access control."""

    def setUp(self):
        """Set up test client and test user."""
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="SecurePass123!")

    ## Signup Tests ##
    def test_signup_with_valid_data(self):
        """Set up test client and test user."""
        response = self.client.post(self.signup_url, {
            "username": "newuser",
            "email": "testemail@email.com",
            "password1": "ValidPass123!",
            "password2": "ValidPass123!",
            "privacy_policy": True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(custom_user.objects.filter(username="newuser").exists())

    def test_signup_with_weak_password(self):
        """Ensure signup fails if password is too weak."""
        response = self.client.post(self.signup_url, {
            "username": "weakuser",
            "email": "testemail@email.com",
            "password1": "weakuser1",
            "password2": "weakuser1",
            "privacy_policy": True
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The password is too similar to the username.") 

    def test_signup_with_mismatched_passwords(self):
        """Ensure signup fails if passwords do not match."""
        response = self.client.post(self.signup_url, {
            "username": "mismatchuser",
            "email": "testemail@email.com",
            "password1": "ValidPass123!",
            "password2": "WrongPass123!",
            "privacy_policy": True
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(custom_user.objects.filter(username="mismatchuser").exists())

    def test_signup_existing_username(self):
        """Test signup fails if username is already taken."""
        response = self.client.post(self.signup_url, {
            'username': 'testuser',
            "email": "testemail@email.com",
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
            "privacy_policy": True
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists.") 

    def test_signup_password_too_short(self):
        """Ensure password is rejected if it's too short."""
        response = self.client.post(self.signup_url, {
            'username': 'shortpassuser',
            "email": "testemail@email.com",
            'password1': '12345',
            'password2': '12345',
            "privacy_policy": True
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is too short")



    ## Login Tests ##
    def test_login_valid_user(self):
        """Ensure a user with correct credentials can log in."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'SecurePass123!'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_password(self):
        """Ensure login fails with incorrect password."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on login page
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Please enter a correct username and password.")

    def test_login_non_existent_user(self):
        """Ensure login fails for a user that doesn't exist."""
        response = self.client.post(self.login_url, {
            'username': 'ghostuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Please enter a correct username and password.")



    ## Logout Tests ##
    def test_logout(self):
        """Ensure a logged-in user can log out successfully."""
        self.client.login(username='testuser', password='SecurePass123!')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Expect redirect after logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)

