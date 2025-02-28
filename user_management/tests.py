from django.test import TestCase
from django.contrib.auth import get_user_model
from user_management.models import UserStats, FriendRequest
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

class FriendRequestTests(TestCase):

    def setUp(self):
        """Set up test users before each test."""
        self.user1 = CustomUser.objects.create_user(username="user1", password="password123")
        self.user2 = CustomUser.objects.create_user(username="user2", password="password123")

    def test_send_friend_request(self):
        """Test if a user can send a friend request."""
        self.user1.send_friend_request(self.user2)
        request = FriendRequest.objects.filter(senderId=self.user1, receiverId=self.user2).first()
        self.assertIsNotNone(request)
        self.assertEqual(request.status, "pending")

    def test_cannot_send_duplicate_friend_request(self):
        """Test that a user cannot send duplicate friend requests if one is already pending."""
        self.user1.send_friend_request(self.user2)
        with self.assertRaises(ValueError):
            self.user1.send_friend_request(self.user2)

    def test_cannot_send_request_to_self(self):
        """Test that a user cannot send a friend request to themselves."""
        with self.assertRaises(ValueError):
            self.user1.send_friend_request(self.user1)

    def test_accept_friend_request(self):
        """Test if a user can accept a friend request and become friends."""
        self.user1.send_friend_request(self.user2)
        self.user2.accept_friend_request(self.user1)

        self.assertTrue(self.user1.friends.filter(pk=self.user2.pk).exists())
        self.assertTrue(self.user2.friends.filter(pk=self.user1.pk).exists())

        request = FriendRequest.objects.filter(senderId=self.user1, receiverId=self.user2).first()
        self.assertIsNone(request)  # Request should be deleted after accepting

    def test_reject_friend_request(self):
        """Test if a user can reject a friend request and prevent new requests."""
        self.user1.send_friend_request(self.user2)
        self.user2.reject_friend_request(self.user1)

        request = FriendRequest.objects.filter(senderId=self.user1, receiverId=self.user2).first()
        self.assertIsNotNone(request)
        self.assertEqual(request.status, "rejected")

        # Ensure the sender cannot send another request after rejection
        with self.assertRaises(ValueError):
            self.user1.send_friend_request(self.user2)

        # However, the receiver can initiate a request
        self.user2.send_friend_request(self.user1)
        request = FriendRequest.objects.filter(senderId=self.user2, receiverId=self.user1).first()
        self.assertIsNotNone(request)
        self.assertEqual(request.status, "pending")

    def test_remove_friend(self):
        """Test if a user can remove a friend and re-send a request later."""
        self.user1.send_friend_request(self.user2)
        self.user2.accept_friend_request(self.user1)
        self.user1.unfriend(self.user2)

        self.assertFalse(self.user1.friends.filter(pk=self.user2.pk).exists())
        self.assertFalse(self.user2.friends.filter(pk=self.user1.pk).exists())

        # Ensure a new request can be sent after unfriending
        self.user1.send_friend_request(self.user2)
        request = FriendRequest.objects.filter(senderId=self.user1, receiverId=self.user2).first()
        self.assertIsNotNone(request)
        self.assertEqual(request.status, "pending")
