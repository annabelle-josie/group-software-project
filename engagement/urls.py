from django.urls import path, include
from . import views

leaderboard_patterns = [
    path("", views.leaderboard, name="leaderboard"),
    path("api/v1/leaderboard", views.get_leaderboard),
]

achievement_patterns = [
    path("", views.achievement, name="achievements"),  # Achievements page
    path('<int:achievement_id>/', views.achievementVisitURL, name='achievement-visit'),
]