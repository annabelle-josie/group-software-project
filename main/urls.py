from django.urls import path, include
from users.urls import auth_patterns, friends_patterns, settings_patterns
from engagement.urls import leaderboard_patterns, achievement_patterns
from . import views

# URL patterns for the main application
urlpatterns = [
    path("", views.home, name="home"),  # Home page
    # path("qr", views.generate_qr, name="qr"),  # QR code generation page

    # path("createchallenge", views.createChallenge, name="createchallenge"),
    # path("save", views.save_image,name="save" ),
    # path("garden/", include("garden.urls")),  # Include garden app URLs

    path("auth/", include(auth_patterns)),
    path("friends/", include(friends_patterns)),
    path("settings/", include(settings_patterns)),
    path("challenges/", include("challenges.urls")),
    path("events/", include("events.urls")),
    path("leaderboard/", include(leaderboard_patterns)),
    path("achievement/", include(achievement_patterns)),

    path("market/", views.market_view, name="market"),  # Market page
 
    path("market/api/add_purchased_plant", views.add_purchased_plant, name="add_purchased_plant"),  # Add purchased plant endpoint

    
    path("profile/<str:username>/", views.profile),
    path("api/get_garden/<int:user_id>/", views.get_garden, name="get_garden"),
    path("updateGarden", views.updateGarden, name="updateGarden"),
    #path('delete_account/', views.delete_account, name='delete_account'),
]