from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Keep home in main
    path("leaderboard", views.leaderboard, name="leaderboard"),
    path("allchallenges", views.challenges, name="allchallenges"),
    path("garden", views.garden, name="garden"),
    path("events", views.events, name="events"),
    path("market", views.market, name="market"),
    path("api/v1/addChallenge", views.add_challenge),
    path("api/v1/removeChallenge", views.remove_challenge),
    path("auth/", include("login.urls")),  # Move login/signup to login app
]