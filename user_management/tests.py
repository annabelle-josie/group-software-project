from django.test import TestCase
from django.contrib.auth import get_user_model
from user_management.models import UserStats, Friendship
from garden.models import Plant, UserGarden

custom_user = get_user_model()

class UserCreationTests(TestCase):

    def setUp(self):
        """Set up test users and Game Keeper group before each test."""
        self.potted_plant = Plant.objects.create(name="Potted Plant", price=10, fact="A simple potted plant.")
        self.user = custom_user.objects.create(username="testuser", password="password123")
        self.game_keeper = custom_user.objects.create(username="gamekeeper", password="securepass")


    
    def test_userstats_creation(self):
        """Ensure a UserStats entry is created when a user is made."""
        stats = UserStats.objects.get(user=self.user)
        self.assertTrue(UserStats.objects.filter(user=self.user).exists())
        self.assertEqual(stats.points, 50)
        self.assertEqual(stats.leaves, 50)

    def test_user_owned_plants_contains_potted_plant(self):
        """Ensure the potted plant is owned by new users."""
        self.assertIn(self.potted_plant, self.user.owned_plants.all())

    def test_user_garden_has_potted_plants_in_all_slots(self):
        """Ensure the user garden exists for the user, and has the potted plant in every slot."""
        user_garden = UserGarden.objects.get(user=self.user)
        self.assertEqual(user_garden.plant1Id, self.potted_plant)
        self.assertEqual(user_garden.plant2Id, self.potted_plant)
        self.assertEqual(user_garden.plant3Id, self.potted_plant)
        self.assertEqual(user_garden.plant4Id, self.potted_plant)
        self.assertEqual(user_garden.plant5Id, self.potted_plant)
        self.assertEqual(user_garden.plant6Id, self.potted_plant)


CustomUser = get_user_model()

class FriendshipTests(TestCase):

    def setUp(self):
        """Create two users for testing friendships."""
        self.user_a = CustomUser.objects.create_user(username="userA", password="testpassword")
        self.user_b = CustomUser.objects.create_user(username="userB", password="testpassword")

    def test_send_friend_request(self):
        """Test sending a friend request."""
        self.user_a.send_friend_request(self.user_b)
        friendship = Friendship.objects.get(user1=self.user_a, user2=self.user_b)
        self.assertEqual(friendship.status, "pending")

    def test_cannot_duplicate_friend_request(self):
        """Ensure users cannot send duplicate friend requests."""
        self.user_a.send_friend_request(self.user_b)
        with self.assertRaises(ValueError):
            self.user_a.send_friend_request(self.user_b)  # Sending again should fail

    def test_cannot_send_request_if_already_friends(self):
        """Ensure users cannot send a request if they are already friends."""
        self.user_a.send_friend_request(self.user_b)
        self.user_b.accept_friend_request(self.user_a)
        with self.assertRaises(ValueError):
            self.user_a.send_friend_request(self.user_b)  # Should fail since they're friends

    def test_cannot_send_request_after_rejection(self):
        """Ensure the rejected sender cannot send another request unless the recipient initiates."""
        self.user_a.send_friend_request(self.user_b)
        self.user_b.reject_friend_request(self.user_a)
        self.user_a.send_friend_request(self.user_b)

        friendship = Friendship.objects.get(user1=self.user_a, user2=self.user_b)
        self.assertEqual(friendship.status, "rejected")

    def test_recipient_can_reverse_rejection(self):
        """Ensure the rejecting recipient can send a request and override rejection."""
        self.user_a.send_friend_request(self.user_b)
        self.user_b.reject_friend_request(self.user_a)
        self.user_b.send_friend_request(self.user_a)

        friendship = Friendship.objects.get(user1=self.user_a, user2=self.user_b)
        self.assertEqual(friendship.status, "pending")

    def test_accept_friend_request(self):
        """Ensure friend requests can be accepted."""
        self.user_a.send_friend_request(self.user_b)
        self.user_b.accept_friend_request(self.user_a)

        friendship = Friendship.objects.get(user1=self.user_a, user2=self.user_b)
        self.assertEqual(friendship.status, "accepted")

    def test_reject_friend_request(self):
        """Ensure friend requests can be rejected."""
        self.user_a.send_friend_request(self.user_b)
        self.user_b.reject_friend_request(self.user_a)

        friendship = Friendship.objects.get(user1=self.user_a, user2=self.user_b)
        self.assertEqual(friendship.status, "rejected")

    def test_get_friends(self):
        """Ensure we can correctly retrieve friends."""
        self.user_a.send_friend_request(self.user_b)
        self.user_b.accept_friend_request(self.user_a)

        accepted_friends = Friendship.objects.filter(status="accepted")
        self.assertEqual(accepted_friends.count(), 1)
        self.assertEqual(accepted_friends.first().user1, self.user_a)
        self.assertEqual(accepted_friends.first().user2, self.user_b)