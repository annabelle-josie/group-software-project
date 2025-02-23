from django.urls import path
from . import views

# URL patterns for the event_management app
urlpatterns = [
    path('', views.event_list, name='event_list'),  
]