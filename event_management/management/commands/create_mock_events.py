import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils import timezone
from django.contrib.auth import get_user_model
from event_management.models import Events

custom_user = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Ensure the event master exists
        event_master, created = custom_user.objects.get_or_create(username="James", email='jb1658@exeter.ac.uk')
        if created:
            event_master.set_password("password7")
            event_master.save()

        events_data = [
            {
                'desc': 'Attend the sustainability event in the SWIOT',
                'title': 'Attend the campus Sustainability event',
                'noOfTasks': 1,
                'rewardValue': 100,
                'startDate': timezone.datetime(2025, 3, 24, 12, 0),
                'endDate': timezone.datetime(2025, 3, 24, 13, 0),
                'eventQR': 'SWIOT Sustainability',
                'eventQRImage': 'static/example_qr_codes/sustainability.png',
                'eventImage': 'static/event_backgrounds/event_background1.gif',
                'isQR': True,
                'eventMaster': event_master
            },
            {
                'desc': 'Go on a walk in 3 different parks during walking week',
                'title': 'Walking Week',
                'noOfTasks': 3,
                'rewardValue': 50,
                'startDate': timezone.datetime(2025, 3, 20, 10, 0),
                'endDate': timezone.datetime(2025, 3, 26, 10, 0),
                'eventQR': 'Walking Week',
                'eventQRImage': 'static/example_qr_codes/walking_week.png',
                'eventImage': 'static/event_backgrounds/event_background2.png',
                'isQR': False,
                'eventMaster': event_master
            },
            {
                'desc': 'Join us litterpicking in the city to make Exeter cleaner',
                'title': 'Litterpicking around Exeter',
                'noOfTasks': 1,
                'rewardValue': 50,
                'startDate': timezone.datetime(2025, 3, 9, 12, 40),
                'endDate': timezone.datetime(2025, 3, 29, 12, 40),
                'eventQR': 'OuweMvQXOmDWWB9gYW9xVCAmR4NBdIq',
                'eventQRImage': 'static/example_qr_codes/litterpicking.png',
                'eventImage': 'static/event_backgrounds/event_background3.gif',
                'isQR': True,
                'eventMaster': event_master
            }
        ]

        for event_data in events_data:
            event, created = Events.objects.get_or_create(
                title=event_data['title'],
                eventMaster=event_data['eventMaster'],
                defaults={
                    'desc': event_data['desc'],
                    'noOfTasks': event_data['noOfTasks'],
                    'rewardValue': event_data['rewardValue'],
                    'startDate': event_data['startDate'],
                    'endDate': event_data['endDate'],
                    'eventQR': event_data['eventQR'],
                    'isQR': event_data['isQR'],
                }
            )
            
            if created:
                try:
                    with open(event_data['eventQRImage'], 'rb') as qr_file, open(event_data['eventImage'], 'rb') as event_file:
                        event.eventQRImage.save("event_qr_image.png", File(qr_file), save=True)
                        event.eventImage.save("event_image.png", File(event_file), save=True)
                    self.stdout.write(self.style.SUCCESS(f"Created event: {event.title}"))
                except Exception:
                    self.stdout.write(self.style.ERROR(f"Error creating event {event_data['title']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Event {event.title} already exists."))
