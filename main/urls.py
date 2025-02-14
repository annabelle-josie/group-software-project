from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Keep home in main
    path("qr", views.generate_qr, name="qr"),  # Keep home in main
    path("leaderboard", views.leaderboard, name="leaderboard"),
    path("allchallenges", views.challenges, name="allchallenges"),
    path("garden/", include("garden.urls")),
    path("events", views.events, name="events"),
    path("market", views.market, name="market"),
    path("api/v1/addChallenge", views.add_challenge),
    path("api/v1/removeChallenge", views.remove_challenge),
    path("auth/", include("login.urls")),  # Move login/signup to login app
]