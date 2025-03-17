from django.urls import path
from . import views

garden_patterns = [
    path("updateGarden", views.updateGarden, name="updateGarden"),
]

market_patterns = [
    path("", views.market_view, name="market"),
    path("api/add_purchased_plant", views.add_purchased_plant, name="add_purchased_plant"),
]