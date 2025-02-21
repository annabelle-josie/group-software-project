from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Keep home in main
    path("qr", views.generate_qr, name="qr"),  # Keep home in main
    path("leaderboard", views.leaderboard, name="leaderboard"),
    path("allchallenges", views.mychallenges, name="allchallenges"),
    path("garden/", include("garden.urls")),
    path("events", views.events, name="events"),
    path("market/", views.market_view, name="market"),
    path("addChallenge", views.add_challenge),
    path("api/v1/addChallenge", views.add_challenge),
    path("api/v1/removeChallenge", views.remove_challenge),
    path("api/v1/removeTask", views.remove_task),
    path("api/v1/leaderboard", views.get_leaderboard),
    path("auth/", include("login.urls")),  # Move login/signup to login app
    path('increment_progress/<int:event_id>/', views.increment_progress, name='increment_progress'),
    path("market/api/add_purchased_plant", views.add_purchased_plant, name="add_purchased_plant"),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
]