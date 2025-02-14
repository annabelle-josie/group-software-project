from django.urls import path
from .views import garden_view, get_garden

urlpatterns = [
    path("", garden_view, name="garden"),
    path("api/get_garden/<int:user_id>/", get_garden, name="get_garden"),
]