from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Keep home in main
    path("qr", views.generate_qr, name="qr"),  # Keep home in main
    path("leaderboard", views.leaderboard, name="leaderboard"),
    path("garden", views.garden, name="garden"),
    path("events", views.events, name="events"),
    path("market", views.market, name="market"),
    path("auth/", include("login.urls")),  # Move login/signup to login app
]