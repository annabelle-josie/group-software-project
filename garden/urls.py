from django.urls import path
from .views import garden_view, get_garden,update_garden

urlpatterns = [
    path("", garden_view, name="garden"),
    path("api/get_garden/<int:user_id>/", get_garden, name="get_garden"),
    path("update_garden", update_garden, name="update_garden"),
    

]