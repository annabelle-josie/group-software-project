import json
import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from events.models import Events, EventParticipants
from engagement.models import UserStats

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

custom_user = get_user_model()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class EventTests(TestCase):
    """Tests for event completion functionality."""

    def setUp(self):
        """Set up test users, events, and event participants before each test."""
        self.client = Client()
        
        self.gamekeeper = custom_user.objects.create_user(username="gamekeeper", email='admintestemail@email.com', password="AdminPass123!")
        gamekeeper_group, _ = Group.objects.get_or_create(name="Game Keepers")
        self.gamekeeper.groups.add(gamekeeper_group)

        self.event = Events.objects.create(
            title="Cleanup Event",
            desc="Pick up trash in the park.",
            noOfTasks=5,
            rewardValue=20,
            startDate=timezone.now(),
            endDate=timezone.now() + timezone.timedelta(days=7),
            eventMaster=self.gamekeeper,
            isQR=False,
        )

        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="SecurePass123!")
        self.user_stats = UserStats.objects.get(user=self.user)
        self.client.login(username="testuser", password="SecurePass123!")

        self.event_participant = EventParticipants.objects.create(
            username=self.user,
            eventId=self.event,
            progress=0,
            status="incomplete"
        )

        self.event_participant = EventParticipants.objects.get(username=self.user, eventId=self.event)

    def tearDown(self):
        """Remove the temporary media directory and all its contents."""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_events_view_shows_user_event(self):
        """Ensure that the events view displays the event details for events the user is participating in."""
        response = self.client.get(reverse("events"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cleanup Event")
        self.assertContains(response, "Pick up trash in the park.")

    def test_user_can_complete_event(self):
        """Ensure a user can complete an event by progressing through all tasks."""
        
        for _ in range(5):
            self.client.post(
                reverse("incrementProgress", args=[self.event.eventId]),
                data=json.dumps({"qrCode": self.event.eventQR}),
                content_type="application/json"
            )

        self.event_participant = EventParticipants.objects.get(username=self.user, eventId=self.event)

        self.assertEqual(self.event_participant.progress, self.event.noOfTasks)
        self.assertEqual(self.event_participant.status, "complete")

        self.user_stats = UserStats.objects.get(user=self.user)

        expected_points = 50 + self.event.rewardValue
        expected_leaves = 50 + self.event.rewardValue
        self.assertEqual(self.user_stats.points, expected_points)
        self.assertEqual(self.user_stats.leaves, expected_leaves)

    def test_gamekeeper_can_create_event(self):
        """Ensure gamekeepers can create events."""
        self.client.login(username="gamekeeper", password="AdminPass123!") 

        response = self.client.post(
            reverse("events"),
            data={
                "title": "New Gamekeeper Event",
                "desc": "A new event created by gamekeeper.",
                "noOfTasks": 3,
                "rewardValue": 35,
                "startDate": timezone.now(),
                "endDate": timezone.now() + timezone.timedelta(days=3),
                "qrCode": "qr"
            }
        )

        self.assertTrue(Events.objects.filter(title="New Gamekeeper Event").exists())

    def test_gamekeeper_can_delete_own_event(self):
        """Ensure gamekeepers can delete their own events."""
        self.client.login(username="gamekeeper", password="AdminPass123!")

        response = self.client.delete(
            reverse("delete_event", args=[self.event.eventId])
        )
        self.assertFalse(Events.objects.filter(eventId=self.event.eventId).exists())

    def test_regular_user_cannot_create_event(self):
        """Ensure regular users cannot create events."""
        self.client.login(username="regularuser", password="UserPass123!")  # Login as a regular user

        response = self.client.post(
            reverse("events"),
            data={
                "title": "Unauthorized Event",
                "desc": "This should not be allowed.",
                "noOfTasks": 2,
                "rewardValue": 40,
                "startDate": timezone.now(),
                "endDate": timezone.now() + timezone.timedelta(days=2),
                "qrCode": "qr"
            }
        )

        self.assertFalse(Events.objects.filter(title="Unauthorized Event").exists())

    def test_regular_user_cannot_delete_event(self):
        """Ensure regular users cannot delete events."""
        self.client.login(username="regularuser", password="UserPass123!")  # Login as a regular user

        response = self.client.delete(
            reverse("delete_event", args=[self.event.eventId])
        )

        self.assertTrue(Events.objects.filter(eventId=self.event.eventId).exists())