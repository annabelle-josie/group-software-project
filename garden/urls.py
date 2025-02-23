from django.urls import path
from .views import gardenView, get_garden,updateGarden

# urlpatterns is a list of URL patterns
urlpatterns = [
    path("", gardenView, name="garden"),
    path("api/get_garden/<int:user_id>/", get_garden, name="get_garden"),
    path("updateGarden", updateGarden, name="updateGarden"),
    

]