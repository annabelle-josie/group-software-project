from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from user_management.models import UserStats, FriendRequest

CustomUser = get_user_model()

class UserStatsTests(TestCase):

    def setUp(self):
        """Set up test users and Game Keeper group before each test."""
        self.user = CustomUser.objects.create(username="testuser", password="password123")
        self.game_keeper = CustomUser.objects.create(username="gamekeeper", password="securepass")

        # Assign Game Keeper to the special group
        game_keeper_group, _ = Group.objects.get_or_create(name="Game Keepers")
        self.game_keeper.groups.add(game_keeper_group)

    def test_userstats_creation(self):
        """Ensure a UserStats entry is created when a user is made."""
        self.assertTrue(UserStats.objects.filter(user=self.user).exists())

    def test_game_keeper_can_award_points(self):
        """Ensure a Game Keeper can award points."""
        self.game_keeper.award_points(self.user, 10)
        self.assertEqual(self.user.stats.points, 10)

    def test_non_game_keeper_cannot_award_points(self):
        """Ensure a normal user cannot award points."""
        with self.assertRaises(PermissionError):
            self.user.award_points(self.game_keeper, 10)

    def test_game_keeper_can_award_leaves(self):
        """Ensure a Game Keeper can award leaves."""
        self.game_keeper.award_leaves(self.user, 5)
        self.assertEqual(self.user.stats.leaves, 5)

    def test_non_game_keeper_cannot_award_leaves(self):
        """Ensure a normal user cannot award leaves."""
        with self.assertRaises(PermissionError):
            self.user.award_leaves(self.game_keeper, 5)



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
