from django.urls import path, include
from . import views

# URL patterns for the main application
urlpatterns = [
    path("", views.home, name="home"),  # Home page
    path("qr", views.generate_qr, name="qr"),  # QR code generation page
    path("leaderboard", views.leaderboard, name="leaderboard"),  # Leaderboard page
    path("allchallenges", views.mychallenges, name="allchallenges"),  # All challenges page
    # path("save", views.save_image,name="save" ),
    path("garden/", include("garden.urls")),  # Include garden app URLs
    path("events", views.events, name="events"),  # Events page
    path("market/", views.market_view, name="market"),  # Market page
    path("addChallenge", views.add_challenge),  # Add challenge endpoint
    path("api/v1/addChallenge", views.add_challenge),  # API endpoint to add challenge
    path("api/v1/removeChallenge", views.remove_challenge),  # API endpoint to remove challenge
    path("api/v1/removeTask", views.remove_task),  # API endpoint to remove task
    path("api/v1/leaderboard", views.get_leaderboard),  # API endpoint to get leaderboard
    path("auth/", include("login.urls")),  # Include login app URLs
    path('increment_progress/<int:event_id>/', views.increment_progress, name='increment_progress'),  # Increment progress endpoint
    path("market/api/add_purchased_plant", views.add_purchased_plant, name="add_purchased_plant"),  # Add purchased plant endpoint
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
]