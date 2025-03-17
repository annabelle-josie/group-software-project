from django.core.files import File
from plants.models import Plant
from django.conf import settings

def get_or_create_default_plant():
    plant_name = "Potted Plant"
    plant_price = 0
    plant_fact = "A common, easy-to-care-for plant often found indoors."
    plant_on_market = False

    static_image_path = "static/system_plants/potted_plant.png"

    default_plant, created = Plant.objects.get_or_create(
        name=plant_name,
        defaults={
            "price": plant_price,
            "fact": plant_fact,
            "onMarket": plant_on_market,
        }
    )
    if created:
        with open(static_image_path, "rb") as f:
            default_plant.image.save("potted_plant.png", File(f), save=True)

    return default_plant
