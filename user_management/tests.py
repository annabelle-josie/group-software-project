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
        self.user_a = CustomUser.objects.create_user(username="userA", email='testemail1@email.com', password="testpassword")
        self.user_b = CustomUser.objects.create_user(username="userB", email='testemail2@email.com', password="testpassword")
        self.user_c = CustomUser.objects.create_user(username="userC", email='testemail3@email.com', password="testpassword")
        self.user_d = CustomUser.objects.create_user(username="userD", email='testemail4@email.com', password="testpassword")

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

        friendship = Friendship.objects.get(user1=self.user_b, user2=self.user_a)
        self.assertEqual(friendship.status, "pending")
        self.assertFalse(Friendship.objects.filter(user1=self.user_a, user2=self.user_b).exists())

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
        """Ensure get_friends() returns only accepted friends."""
        Friendship.objects.create(user1=self.user_a, user2=self.user_b, status="accepted")
        Friendship.objects.create(user1=self.user_a, user2=self.user_c, status="accepted")
        Friendship.objects.create(user1=self.user_d, user2=self.user_a, status="pending")

        friends = self.user_a.get_friends()

        self.assertEqual(friends.count(), 2)
        self.assertIn(self.user_b, friends)
        self.assertIn(self.user_c, friends)
        self.assertNotIn(self.user_d, friends)


    def test_get_incoming_friend_requests(self):
        """Ensure get_incoming_friend_requests() returns only pending requests."""
        Friendship.objects.create(user1=self.user_a, user2=self.user_b, status="accepted")
        Friendship.objects.create(user1=self.user_a, user2=self.user_c, status="accepted")
        Friendship.objects.create(user1=self.user_d, user2=self.user_a, status="pending")

        incoming_requests = self.user_a.get_incoming_friend_requests()

        self.assertEqual(incoming_requests.count(), 1)
        self.assertIn(self.user_d, incoming_requests)
        self.assertNotIn(self.user_b, incoming_requests)
        self.assertNotIn(self.user_c, incoming_requests)

    def test_unfriend(self):
        """Ensure users can unfriend each other."""
        Friendship.objects.create(user1=self.user_a, user2=self.user_b, status="accepted")
        result = self.user_a.unfriend(self.user_b)

        self.assertTrue(result)
        self.assertFalse(Friendship.objects.filter(user1=self.user_a, user2=self.user_b).exists())
