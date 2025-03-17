from django.urls import path, include
from users.urls import auth_patterns, friends_patterns, settings_patterns
from engagement.urls import leaderboard_patterns, achievement_patterns
from plants.urls import garden_patterns, market_patterns
from . import views

# URL patterns for the main application
urlpatterns = [
    path("", views.home, name="home"),
    path("auth/", include(auth_patterns)),
    path("friends/", include(friends_patterns)),
    path("plants/", include(garden_patterns)),
    path("challenges/", include("challenges.urls")),
    path("events/", include("events.urls")),
    path("market/", include(market_patterns)),
    path("leaderboard/", include(leaderboard_patterns)),
    path("achievement/", include(achievement_patterns)),
    path("settings/", include(settings_patterns)),
]