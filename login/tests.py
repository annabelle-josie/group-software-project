from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class LoginTests(TestCase):
    def setUp(self):
        """Set up test client and test user."""
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(username='testuser', password='SecurePass123!')

    ## Signup Tests ##
    def test_signup_valid_user(self):
        """Test user can sign up successfully with valid credentials."""
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect on success
        self.assertTrue(User.objects.filter(username='newuser').exists())  # User should be created

    def test_signup_password_mismatch(self):
        """Test signup fails if passwords don’t match."""
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password1': 'Password123',
            'password2': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on signup page
        self.assertFalse(User.objects.filter(username='newuser').exists())  # User should not be created

    def test_signup_existing_username(self):
        """Test signup fails if username is already taken."""
        response = self.client.post(self.signup_url, {
            'username': 'testuser',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists.") 

    def test_signup_password_too_short(self):
        """Ensure password is rejected if it's too short."""
        response = self.client.post(self.signup_url, {
            'username': 'shortpassuser',
            'password1': '12345',
            'password2': '12345'
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

    ## Protected Views (Test only after admin pages exist) ##
    # def test_protected_view_requires_login(self):
    #     """Ensure a protected page redirects anonymous users."""
    #     protected_url = reverse('home') # Change later to an admin page
    #     response = self.client.get(protected_url)
    #     self.assertNotEqual(response.status_code, 200)  # Should redirect

    # def test_protected_view_accessible_to_logged_in_users(self):
    #     """Ensure a logged-in user can access a protected page."""
    #     protected_url = reverse('home')  # Change later to an admin page
    #     self.client.login(username='testuser', password='SecurePass123!')
    #     response = self.client.get(protected_url)
    #     self.assertEqual(response.status_code, 200)