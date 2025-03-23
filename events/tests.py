import json
import shutil
import tempfile
import secrets
import string
from io import BytesIO
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from events.models import Events, EventParticipants
from engagement.models import UserStats
from plants.models import Plant


custom_user = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class EventCreationTests(TestCase):

    def setUp(self):
        """Set up test users before each test."""
        self.client = Client()
        
        self.gamekeeper = custom_user.objects.create_user(username="gamekeeper", email='admintestemail@email.com', password="AdminPass123!")
        gamekeeper_group, _ = Group.objects.get_or_create(name="Game Keepers")
        self.gamekeeper.groups.add(gamekeeper_group)

        self.user = custom_user.objects.create_user(username="testuser", email="testemail@email.com", password="SecurePass123!")
        self.user_stats = UserStats.objects.get(user=self.user)

    def tearDown(self):
        """Remove the temporary media directory and all its contents."""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()

    def test_gamekeeper_can_create_event(self):
        """Test if gamekeepers can create events."""
        self.client.login(username="gamekeeper", password="AdminPass123!") 

        response = self.client.post(
            reverse("events"),
            data={
                "title": "New Gamekeeper Event",
                "desc": "A new event created by gamekeeper.",
                "noOfTasks": 1,
                "rewardValue": 35,
                "startDate": timezone.now(),
                "endDate": timezone.now() + timezone.timedelta(days=3),
                "qrCode": "non-qr"
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Events.objects.filter(title="New Gamekeeper Event").exists())

    def test_gamekeeper_can_create_qr_event(self):
        """Test if gamekeepers can create a QR event."""
        self.client.login(username="gamekeeper", password="AdminPass123!")
                        
        response = self.client.post(
            reverse("events"), 
            data={
                "title": "QR Gamekeeper Event",
                "desc": "A qr event created by gamekeeper.",
                "noOfTasks": 1,
                "rewardValue": 30,
                "startDate": timezone.now().isoformat(),
                "endDate": timezone.now() + timezone.timedelta(days=3),
                "qrCode": "qr",
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Events.objects.filter(title="QR Gamekeeper Event").exists())

    def test_gamekeeper_can_create_plant_reward_event(self):
        """Test if gamekeepers can create an even with a plant reward."""
        self.client.login(username="gamekeeper", password="AdminPass123!")
        # Create a plant reward to assign to the event.
        plant = Plant.objects.create(
            name="Sunflower", price=10, fact="A bright yellow flower.", onMarket=True
        )
        response = self.client.post(
            reverse("events"), 
            data={
                "title": "Plant Reward Gamekeeper Event",
                "desc": "An event created by gamekeeper that rewards a plant.",
                "noOfTasks": 1,
                "rewardValue": 30,
                "startDate": timezone.now().isoformat(),
                "endDate": timezone.now() + timezone.timedelta(days=3),
                "qrCode": "non-qr",
                "plantReward": plant.id
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Events.objects.filter(title="Plant Reward Gamekeeper Event").exists())

    def test_gamekeeper_can_delete_own_event(self):
        """Test if gamekeepers can delete events they created."""
        self.client.login(username="gamekeeper", password="AdminPass123!")
        event = Events.objects.create(
            title="Deletable Event",
            desc="An event created for deletion test.",
            noOfTasks=3,
            rewardValue=25,
            startDate=timezone.now(),
            endDate=timezone.now() + timezone.timedelta(days=3),
            isQR=False,
            eventMaster=self.gamekeeper,
        )
        response = self.client.delete(reverse("delete_event", args=[event.eventId]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Events.objects.filter(eventId=event.eventId).exists())

    def test_regular_user_cannot_create_event(self):
        """Ensure regular users cannot create events."""
        self.client.login(username="regularuser", password="UserPass123!")

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
        """Regular users cannot delete events."""
        self.client.login(username="regularuser", password="UserPass123!")
        event = Events.objects.create(
            title="Protected Event",
            desc="This event should not be deletable by regular users.",
            noOfTasks=2,
            rewardValue=20,
            startDate=timezone.now(),
            endDate=timezone.now() + timezone.timedelta(days=2),
            isQR=False,
            eventMaster=self.gamekeeper,
        )
        response = self.client.delete(reverse("delete_event", args=[event.eventId]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Events.objects.filter(eventId=event.eventId).exists())


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class EventFunctionalityTests(TestCase):

    def setUp(self):
        """Set up test users, events, and event participants before each test."""
        self.client = Client()

        self.gamekeeper = custom_user.objects.create_user(username="gamekeeper", email="gk@example.com", password="AdminPass123!")
        gamekeeper_group, _ = Group.objects.get_or_create(name="Game Keepers")
        self.gamekeeper.groups.add(gamekeeper_group)

        self.event = Events.objects.create(
            title="Cleanup Event",
            desc="Pick up trash in the park.",
            noOfTasks=5,
            rewardValue=20,
            startDate=timezone.now(),
            endDate=timezone.now() + timezone.timedelta(days=7),
            isQR=False,
            eventMaster=self.gamekeeper,
        )

        self.qr_event = Events.objects.create(
            title="QR Recycling Challenge",
            desc="Scan the QR code at the recycling bin.",
            noOfTasks=3,
            rewardValue=30,
            startDate=timezone.now(),
            endDate=timezone.now() + timezone.timedelta(days=3),
            isQR=True,
            eventQR="TESTQR123",
            eventMaster=self.gamekeeper,
        )

        self.user = custom_user.objects.create_user(username="testuser", email="testuser@example.com", password="password123")
        self.user_stats = UserStats.objects.get(user=self.user)

        self.nonqr_participant = EventParticipants.objects.create(
            username=self.user,
            eventId=self.event,
            progress=0,
            status="incomplete"
        )

        self.qr_participant = EventParticipants.objects.create(
            username=self.user,
            eventId=self.qr_event,
            progress=0,
            status="incomplete"
        )

    def tearDown(self):
        """Remove the temporary media directory and all its contents."""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDown()
    
    def test_shows_user_events(self):
        """Ensure the events view displays events the user is signed up for."""
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("events"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cleanup Event")
        self.assertContains(response, "QR Recycling Challenge")

    def test_increment_progress_nonqr_event(self):
        """Test that incrementing progress works for a non-QR event."""
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("incrementProgress", args=[self.event.eventId]),
            data=json.dumps({"qrCode": None}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        updated_participant = EventParticipants.objects.get(username=self.user, eventId=self.event)
        self.assertEqual(updated_participant.progress, 1)

    def test_increment_progress_qr_event_correct_qr(self):
        """Test that scanning the correct QR code for a QR event increments progress."""
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("scan_qr", args=[self.qr_event.eventId, "TESTQR123"]),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        updated_participant = EventParticipants.objects.get(username=self.user, eventId=self.qr_event)
        self.assertEqual(updated_participant.progress, 1)

    def test_increment_progress_qr_event_incorrect_qr(self):
        self.client.login(username="testuser", password="password123")
        """Test that scanning an incorrect QR code for a QR event returns an error and does not increment progress."""
        response = self.client.post(
            reverse("scan_qr", args=[self.qr_event.eventId, "WRONGQR"]),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        updated_participant = EventParticipants.objects.get(username=self.user, eventId=self.qr_event)
        self.assertEqual(updated_participant.progress, 0)

    def test_event_completion_rewards(self):
        """Test that completing an event awards the correct points leaves, and the plant reward."""
        plant_reward = Plant.objects.create(
            name="Rose",
            price=60,
            fact="A flower.",
            onMarket=True
        )

        event_with_plant = Events.objects.create(
            title="Floral Challenge",
            desc="Complete this challenge and earn a beautiful rose as a reward.",
            noOfTasks=3,
            rewardValue=30,
            startDate=timezone.now(),
            endDate=timezone.now() + timezone.timedelta(days=3),
            isQR=False,
            eventMaster=self.gamekeeper,
            plantReward=plant_reward
        )

        EventParticipants.objects.create(
            username=self.user,
            eventId=event_with_plant,
            progress=0,
            status="incomplete"
        )

        self.client.login(username="testuser", password="password123")

        for _ in range(event_with_plant.noOfTasks):
            self.client.post(
                reverse("incrementProgress", args=[event_with_plant.eventId]),
                content_type="application/json",
                data=json.dumps({"qrCode": None})
            )

        updated_participant = EventParticipants.objects.get(username=self.user, eventId=event_with_plant)
        self.assertEqual(updated_participant.status, "complete")
        self.user_stats.refresh_from_db()
        
        expected_points = 50 + event_with_plant.rewardValue
        expected_leaves = 50 + event_with_plant.rewardValue

        self.assertEqual(self.user_stats.points, expected_points)
        self.assertEqual(self.user_stats.leaves, expected_leaves)
        self.assertIn(plant_reward, self.user.owned_plants.all())
