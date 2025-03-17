from django.core.management.base import BaseCommand
from django.core.files import File
from plants.models import Plant

class Command(BaseCommand):
    def handle(self, *args, **options):
        plants_data = [
            {"name": "Potted Plant", "fact": "A common, easy-to-care-for plant often found indoors.", "price": 0, "onMarket": False},
            {"name": "Little Pink Cactus", "fact": "A cute, small cactus with vibrant pink spines.", "price": 30, "onMarket": True},
            {"name": "Rose", "fact": "Roses are a symbol of love and are known for their fragrant blooms.", "price": 40, "onMarket": True},
            {"name": "Chrysanthemum", "fact": "Often used in fall decorations, chrysanthemums come in many colors.", "price": 35, "onMarket": True},
            {"name": "Daffodil", "fact": "Daffodils bloom in early spring and symbolize new beginnings.", "price": 30, "onMarket": True},
            {"name": "Yellow Poppy", "fact": "A beautiful wildflower with bright yellow petals that bloom in the spring.", "price": 45, "onMarket": True},
            {"name": "Cattail", "fact": "Cattails are commonly found in wetlands and are known for their brown, furry spikes.", "price": 50, "onMarket": True},
            {"name": "Snapdragon", "fact": "Known for its dragon-shaped flowers, snapdragons come in many colors.", "price": 40, "onMarket": True},
            {"name": "Amaryllis", "fact": "Amaryllis flowers bloom in winter, producing large, beautiful blooms.", "price": 60, "onMarket": True},
            {"name": "Lilac", "fact": "Lilacs are known for their sweet scent and are often purple or white in color.", "price": 50, "onMarket": True},
            {"name": "Sunflower", "fact": "Sunflowers are known for their bright, yellow petals and large, seed-filled heads.", "price": 35, "onMarket": True},
            {"name": "Long Stem Plant", "fact": "A tall plant with long, elegant stems, perfect for decorative arrangements.", "price": 55, "onMarket": True},
            {"name": "Large Palm", "fact": "Large palms are great for adding a tropical feel to your space.", "price": 70, "onMarket": True},
            {"name": "Cactus", "fact": "Cacti are low-maintenance plants that thrive in dry, arid environments.", "price": 60, "onMarket": True},
            {"name": "Flower Cactus", "fact": "A cactus that produces flowers, often in vibrant hues.", "price": 75, "onMarket": True},
            {"name": "Fern", "fact": "Ferns are ancient plants that thrive in shady, moist environments.", "price": 25, "onMarket": True},
        ]

        for plant_data in plants_data:
            image_path = f"static/system_plants/{plant_data['name'].replace(' ', '_').lower()}.png"
            
            plant, created = Plant.objects.get_or_create(
                name=plant_data["name"],
                defaults={
                    "price": plant_data["price"],
                    "fact": plant_data["fact"],
                    "onMarket": plant_data["onMarket"],
                }
            )
            
            if created:
                with open(image_path, 'rb') as f:
                    plant.image.save(f"{plant_data['name']}_image.png", File(f), save=True)

                self.stdout.write(self.style.SUCCESS(f"Created plant: {plant.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"{plant.name} already exists."))
