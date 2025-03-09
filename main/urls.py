from django.urls import path, include
from . import views

# URL patterns for the main application
urlpatterns = [
    path("", views.home, name="home"),  # Home page
    # path("qr", views.generate_qr, name="qr"),  # QR code generation page
    path("leaderboard", views.leaderboard, name="leaderboard"),  # Leaderboard page
    path("allchallenges", views.my_challenges, name="allchallenges"),  # All challenges page
    # path("createchallenge", views.createChallenge, name="createchallenge"),
    # path("save", views.save_image,name="save" ),
    # path("garden/", include("garden.urls")),  # Include garden app URLs
    path("events", views.events, name="events"),  # Events page
    path("market/", views.market_view, name="market"),  # Market page
    # path("addChallenge", views.add_challenge),  # Add challenge endpoint
    # path("api/v1/addChallenge", views.add_challenge),  # API endpoint to add challenge
    path("api/v1/removeChallenge", views.remove_challenge),  # API endpoint to remove challenge
    path("api/v1/removeTask", views.remove_task),  # API endpoint to remove task
    path("api/v1/leaderboard", views.get_leaderboard),  # API endpoint to get leaderboard
    path("auth/", include("login.urls")),  # Include login app URLs
    path('incrementProgress/<int:event_id>/', views.incrementProgress, name='incrementProgress'),  # Increment progress endpoint
    path("market/api/add_purchased_plant", views.add_purchased_plant, name="add_purchased_plant"),  # Add purchased plant endpoint
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('challenge_increment_progress/<int:challenge_Id>', views.challenge_increment_progress, name='challenge_increment_progress'),
    path("profile/<str:username>/", views.profile),
    path('sign_up_for_event/<int:event_id>/', views.sign_up_for_event, name='sign_up_for_event'),
    path('settings/', views.settings, name='settings'),
    path("api/get_garden/<int:user_id>/", views.get_garden, name="get_garden"),
    path("updateGarden", views.updateGarden, name="updateGarden"),
    path('scan-qr/<int:event_id>/<str:qr_code>/', views.scan_qr, name='scan_qr')

]